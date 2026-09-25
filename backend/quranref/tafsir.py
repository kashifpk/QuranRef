"""Tafsir (commentary) import and API.

QUL exports a tafsir as JSON keyed by aya: the value is either an object with ``text`` and
``ayah_keys`` (a passage that may cover several ayas) or a string naming the aya whose
passage covers this one. The passages go into ``tafsir_texts`` and every aya they cover into
``tafsir_entries``, so a lookup by aya is one indexed read.
"""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .ayatext import aya_sort_key
from .db import get_session
from .schemas import TafsirPassageSchema, TafsirResourceSchema
from .sql_models import TafsirEntry, TafsirResource, TafsirText

router = APIRouter(tags=["tafsir"])


def parse_qul_tafsir(data: dict) -> list[tuple[list[str], str]]:
    """Passages as (aya_keys, text) from a QUL tafsir JSON document."""
    passages: list[tuple[list[str], str]] = []
    covered: set[str] = set()
    for key, value in data.items():
        if not isinstance(value, dict):
            continue  # a pointer to the passage that covers this aya
        text = (value.get("text") or "").strip()
        keys = [str(k) for k in (value.get("ayah_keys") or [key])]
        if key not in keys:
            keys.insert(0, key)
        keys = sorted(set(keys), key=aya_sort_key)
        if not text:
            continue
        passages.append((keys, text))
        covered.update(keys)
    # A pointer whose target has no passage of its own is dropped; pointers are otherwise
    # already implied by the target's ayah_keys.
    for key, value in data.items():
        if isinstance(value, str) and value in covered and key not in covered:
            for keys, _text in passages:
                if value in keys:
                    keys.append(key)
                    keys.sort(key=aya_sort_key)
                    covered.add(key)
                    break
    passages.sort(key=lambda p: aya_sort_key(p[0][0]))
    return passages


def import_tafsir(
    session: Session,
    file_path: Path,
    slug: str,
    name: str,
    language: str,
    author: str = "",
    source: str = "",
    license: str = "",
) -> tuple[int, int]:
    """Load a QUL tafsir JSON file, replacing any earlier import with the same slug.

    Returns (passages, ayas covered).
    """
    with open(file_path, encoding="utf-8") as fp:
        data = json.load(fp)
    passages = parse_qul_tafsir(data)

    resource = session.execute(
        select(TafsirResource).where(TafsirResource.slug == slug)
    ).scalar_one_or_none()
    if resource is None:
        resource = TafsirResource(slug=slug, name=name, language=language)
        session.add(resource)
    resource.name, resource.language = name, language
    resource.author, resource.source, resource.license = author, source, license
    session.flush()
    session.execute(delete(TafsirText).where(TafsirText.resource_id == resource.id))

    entries = 0
    for keys, text in passages:
        passage = TafsirText(
            resource_id=resource.id, from_key=keys[0], to_key=keys[-1], aya_keys=keys, text=text
        )
        session.add(passage)
        session.flush()
        session.add_all(
            TafsirEntry(resource_id=resource.id, aya_key=k, text_id=passage.id) for k in keys
        )
        entries += len(keys)
    session.commit()
    return len(passages), entries


@router.get("/tafsirs")
def list_tafsirs(session: Session = Depends(get_session)) -> list[TafsirResourceSchema]:
    rows = (
        session.execute(
            select(TafsirResource).order_by(TafsirResource.language, TafsirResource.name)
        )
        .scalars()
        .all()
    )
    return [TafsirResourceSchema.model_validate(r) for r in rows]


@router.get("/tafsir/{slug}/{aya_key}")
def get_tafsir(
    slug: str, aya_key: str, session: Session = Depends(get_session)
) -> TafsirPassageSchema:
    """The passage of the given tafsir that covers the aya, with the range it covers."""
    row = session.execute(
        select(TafsirResource, TafsirText)
        .join(TafsirEntry, TafsirEntry.resource_id == TafsirResource.id)
        .join(TafsirText, TafsirText.id == TafsirEntry.text_id)
        .where(TafsirResource.slug == slug, TafsirEntry.aya_key == aya_key)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tafsir for this aya")
    resource, passage = row
    return TafsirPassageSchema(
        slug=resource.slug,
        name=resource.name,
        language=resource.language,
        aya_key=aya_key,
        from_key=passage.from_key,
        to_key=passage.to_key,
        aya_keys=list(passage.aya_keys),
        text=passage.text,
    )
