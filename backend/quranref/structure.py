"""Mushaf structure API: juz, hizb, rub, manzil, ruku, sajda and surah descriptions."""

import json

from age_orm import Graph
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_session, graph, raw_connection
from .schemas import AyaStructureSchema, SurahInfoSchema, SurahMarkerSchema
from .sql_models import SurahInfo

router = APIRouter(tags=["structure"])

_FIELDS = ["aya_number", "juz", "hizb", "rub", "manzil", "ruku", "surah_ruku", "sajda"]


def _scalar(value):
    return None if value == {} else value


@router.get("/structure")
def get_structure() -> dict[str, list[dict]]:
    """The juz, hizb, rub, manzil and ruku tables, each with the surah ranges it covers."""
    with raw_connection() as conn:
        row = conn.execute("SELECT value FROM meta_info WHERE key = %s", ("structure",)).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Structure not imported")
    value = row[0]
    return json.loads(value) if isinstance(value, str) else value


@router.get("/structure/aya/{aya_key}")
def get_aya_structure(aya_key: str, g: Graph = Depends(graph)) -> AyaStructureSchema:
    rows = g.cypher(
        "MATCH (a:Aya {id: $key}) RETURN a.id, a.juz, a.hizb, a.rub, a.manzil, a.ruku, "
        "a.surah_ruku, a.sajda",
        columns=["aya_key", "juz", "hizb", "rub", "manzil", "ruku", "surah_ruku", "sajda"],
        key=aya_key,
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aya not found")
    return AyaStructureSchema(**{k: _scalar(v) for k, v in rows[0].items()})


@router.get("/structure/surah/{surah_number}")
def get_surah_markers(surah_number: int, g: Graph = Depends(graph)) -> list[SurahMarkerSchema]:
    """Ayas of a surah where a juz, hizb, rub or ruku begins, or that carry a sajda."""
    rows = g.cypher(
        "MATCH (s:Surah {id: $sid})-[:HAS_AYA]->(a:Aya) WHERE a.aya_number > 0 "
        "RETURN a.aya_number, a.juz, a.hizb, a.rub, a.manzil, a.ruku, a.surah_ruku, a.sajda",
        columns=_FIELDS,
        sid=str(surah_number),
    )
    ayas = sorted(
        ({k: _scalar(v) for k, v in r.items()} for r in rows), key=lambda r: r["aya_number"]
    )
    markers = []
    previous: dict = {}
    for a in ayas:
        marker = SurahMarkerSchema(aya_number=a["aya_number"], sajda=a["sajda"])
        for unit in ("juz", "hizb", "rub", "manzil"):
            if a[unit] is not None and a[unit] != previous.get(unit):
                setattr(marker, f"{unit}_start", a[unit])
        if a["surah_ruku"] is not None and a["surah_ruku"] != previous.get("surah_ruku"):
            marker.ruku_start = a["surah_ruku"]
        if marker.sajda or any(
            getattr(marker, f"{u}_start") for u in ("juz", "hizb", "rub", "manzil", "ruku")
        ):
            markers.append(marker)
        previous = a
    return markers


@router.get("/surah-info/{surah_number}")
def get_surah_info(
    surah_number: int,
    language: str = Query("english"),
    session: Session = Depends(get_session),
) -> SurahInfoSchema:
    rows = (
        session.execute(select(SurahInfo).where(SurahInfo.surah_number == surah_number))
        .scalars()
        .all()
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No description")
    available = sorted(r.language for r in rows)
    chosen = next((r for r in rows if r.language == language), rows[0])
    return SurahInfoSchema(
        surah_number=surah_number,
        language=chosen.language,
        available=available,
        text=chosen.text,
        short_text=chosen.short_text,
    )
