"""Related verses API: similar ayas and recurring phrases."""

from age_orm import Graph
from fastapi import APIRouter, Depends, HTTPException, Query, status

from .ayatext import aya_sort_key, ayas_with_texts
from .db import graph
from .schemas import AyaPageSchema, PhraseSchema, RelatedSchema, SimilarAyaSchema

router = APIRouter(tags=["related"])


def _scalar(value):
    return None if value == {} else value


@router.get("/related/{aya_key}")
def get_related(
    aya_key: str, languages: str = Query("arabic:simple"), g: Graph = Depends(graph)
) -> RelatedSchema:
    """Ayas similar to this one (either direction) and the phrases it shares with others."""
    rows = g.cypher(
        "MATCH (a:Aya {id: $key})-[s:SIMILAR_TO]-(b:Aya) "
        "RETURN b.id, s.score, s.coverage, s.matched_words, s.match_words",
        columns=["aya_key", "score", "coverage", "matched_words", "match_words"],
        key=aya_key,
    )
    similar: dict[str, SimilarAyaSchema] = {}
    for r in rows:
        if r["aya_key"] == aya_key:
            continue
        current = similar.get(r["aya_key"])
        if current is None or (r["score"] or 0) > current.score:
            similar[r["aya_key"]] = SimilarAyaSchema(
                aya_key=r["aya_key"],
                score=r["score"] or 0,
                coverage=r["coverage"] or 0,
                matched_words=r["matched_words"] or 0,
                match_words=_scalar(r["match_words"]) or [],
            )
    ordered = sorted(similar.values(), key=lambda s: (-s.score, aya_sort_key(s.aya_key)))
    texts = {
        a.aya_key: a.texts for a in ayas_with_texts(g, [s.aya_key for s in ordered], languages)
    }
    for s in ordered:
        s.texts = texts.get(s.aya_key, {})

    phrase_rows = g.cypher(
        "MATCH (a:Aya {id: $key})-[h:HAS_PHRASE]->(p:Phrase) "
        "RETURN p.id, p.text, p.source_aya, p.aya_count, h.ranges",
        columns=["id", "text", "source_aya", "aya_count", "ranges"],
        key=aya_key,
    )
    phrases = [
        PhraseSchema(
            id=r["id"],
            text=r["text"],
            source_aya=r["source_aya"],
            aya_count=r["aya_count"] or 0,
            ranges=_scalar(r["ranges"]) or [],
        )
        for r in phrase_rows
    ]
    phrases.sort(key=lambda p: -p.aya_count)
    return RelatedSchema(similar=ordered, phrases=phrases)


@router.get("/phrase/{phrase_id}")
def get_phrase(phrase_id: str, g: Graph = Depends(graph)) -> PhraseSchema:
    rows = g.cypher(
        "MATCH (p:Phrase {id: $id}) OPTIONAL MATCH (a:Aya)-[:HAS_PHRASE]->(p) "
        "RETURN p.id, p.text, p.source_aya, p.aya_count, a.id",
        columns=["id", "text", "source_aya", "aya_count", "aya_key"],
        id=phrase_id,
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phrase not found")
    keys = sorted({_scalar(r["aya_key"]) for r in rows if _scalar(r["aya_key"])}, key=aya_sort_key)
    return PhraseSchema(
        id=rows[0]["id"],
        text=rows[0]["text"],
        source_aya=rows[0]["source_aya"],
        aya_count=rows[0]["aya_count"] or 0,
        aya_keys=keys,
    )


@router.get("/phrase/{phrase_id}/ayas")
def get_phrase_ayas(
    phrase_id: str,
    languages: str = Query("arabic:simple"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    g: Graph = Depends(graph),
) -> AyaPageSchema:
    rows = g.cypher(
        "MATCH (a:Aya)-[:HAS_PHRASE]->(p:Phrase {id: $id}) RETURN a.id",
        columns=["aya_key"],
        id=phrase_id,
    )
    keys = sorted({r["aya_key"] for r in rows}, key=aya_sort_key)
    page = keys[offset : offset + limit]
    return AyaPageSchema(total=len(keys), offset=offset, ayas=ayas_with_texts(g, page, languages))
