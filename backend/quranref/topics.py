"""Topics and themes API."""

import re
from collections import defaultdict

from age_orm import Graph
from fastapi import APIRouter, Depends, HTTPException, Query, status

from .ayatext import aya_sort_key, ayas_with_texts
from .db import graph
from .schemas import AyaPageSchema, AyaTopicsSchema, ThemeSchema, TopicSchema, TopicSummarySchema

router = APIRouter(tags=["topics"])

_TOPIC_LINK = re.compile(r'<topic data-id="(\d+)">')


def _scalar(value):
    return None if value == {} else value


def _summary(r: dict) -> TopicSummarySchema:
    return TopicSummarySchema(
        id=r["id"],
        name=r["name"],
        arabic_name=_scalar(r.get("arabic_name")) or "",
        aya_count=r.get("aya_count") or 0,
        thematic=bool(r.get("thematic")),
        ontology=bool(r.get("ontology")),
        parent_id=_scalar(r.get("parent_id")),
        thematic_parent_id=_scalar(r.get("thematic_parent_id")),
        ontology_parent_id=_scalar(r.get("ontology_parent_id")),
    )


def _render_description(html: str) -> str:
    """Turn QUL's <topic data-id> cross-links into app links."""
    return _TOPIC_LINK.sub(r'<a href="/topic/\1" class="topic-link">', html or "").replace(
        "</topic>", "</a>"
    )


@router.get("/topics")
def list_topics(g: Graph = Depends(graph)) -> list[TopicSummarySchema]:
    """Every topic with its parents in each hierarchy; the client builds the trees."""
    rows = g.cypher(
        "MATCH (t:Topic) OPTIONAL MATCH (t)-[c:CHILD_OF]->(p:Topic) "
        "RETURN t.id, t.name, t.arabic_name, t.aya_count, t.thematic, t.ontology, c.kind, p.id",
        columns=[
            "id",
            "name",
            "arabic_name",
            "aya_count",
            "thematic",
            "ontology",
            "kind",
            "parent",
        ],
    )
    topics: dict[str, dict] = {}
    for r in rows:
        t = topics.setdefault(r["id"], dict(r))
        kind, parent = _scalar(r["kind"]), _scalar(r["parent"])
        if kind and parent:
            t[
                {
                    "parent": "parent_id",
                    "thematic": "thematic_parent_id",
                    "ontology": "ontology_parent_id",
                }[kind]
            ] = parent
    result = [_summary(t) for t in topics.values()]
    result.sort(key=lambda t: t.name.lower())
    return result


@router.get("/topic/{topic_id}")
def get_topic(topic_id: str, g: Graph = Depends(graph)) -> TopicSchema:
    rows = g.cypher(
        "MATCH (t:Topic {id: $id}) RETURN t.id, t.name, t.arabic_name, t.description, "
        "t.wiki_link, t.thematic, t.ontology, t.aya_count",
        columns=[
            "id",
            "name",
            "arabic_name",
            "description",
            "wiki_link",
            "thematic",
            "ontology",
            "aya_count",
        ],
        id=topic_id,
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    t = rows[0]

    def neighbours(pattern: str) -> list[TopicSummarySchema]:
        found = g.cypher(
            f"MATCH (t:Topic {{id: $id}}){pattern}(o:Topic) "
            "RETURN DISTINCT o.id, o.name, o.arabic_name, o.aya_count, o.thematic, o.ontology",
            columns=["id", "name", "arabic_name", "aya_count", "thematic", "ontology"],
            id=topic_id,
        )
        return sorted((_summary(r) for r in found), key=lambda x: x.name.lower())

    return TopicSchema(
        id=t["id"],
        name=t["name"],
        arabic_name=_scalar(t["arabic_name"]) or "",
        description=_render_description(_scalar(t["description"]) or ""),
        wiki_link=_scalar(t["wiki_link"]) or "",
        thematic=bool(t["thematic"]),
        ontology=bool(t["ontology"]),
        aya_count=t["aya_count"] or 0,
        parents=neighbours("-[:CHILD_OF]->"),
        children=neighbours("<-[:CHILD_OF]-"),
        related=neighbours("-[:RELATED_TOPIC]-"),
    )


def _page_of_ayas(
    g: Graph, aya_keys: list[str], languages_spec: str, offset: int, limit: int
) -> AyaPageSchema:
    keys = sorted(set(aya_keys), key=aya_sort_key)
    page = keys[offset : offset + limit]
    return AyaPageSchema(
        total=len(keys), offset=offset, ayas=ayas_with_texts(g, page, languages_spec)
    )


@router.get("/topic/{topic_id}/ayas")
def get_topic_ayas(
    topic_id: str,
    languages: str = Query("arabic:simple"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    g: Graph = Depends(graph),
) -> AyaPageSchema:
    """A page of the ayas about a topic, with texts in the requested languages."""
    rows = g.cypher(
        "MATCH (a:Aya)-[:HAS_TOPIC]->(t:Topic {id: $id}) RETURN a.id",
        columns=["aya_key"],
        id=topic_id,
    )
    return _page_of_ayas(g, [r["aya_key"] for r in rows], languages, offset, limit)


@router.get("/aya-topics/{aya_key}")
def get_aya_topics(aya_key: str, g: Graph = Depends(graph)) -> AyaTopicsSchema:
    """Topics and themes an aya belongs to."""
    topics = g.cypher(
        "MATCH (a:Aya {id: $key})-[:HAS_TOPIC]->(t:Topic) "
        "RETURN t.id, t.name, t.arabic_name, t.aya_count, t.thematic, t.ontology",
        columns=["id", "name", "arabic_name", "aya_count", "thematic", "ontology"],
        key=aya_key,
    )
    themes = g.cypher(
        "MATCH (a:Aya {id: $key})-[:HAS_THEME]->(th:Theme) "
        "RETURN th.id, th.theme, th.surah_number, th.aya_from, th.aya_to, th.keywords",
        columns=["id", "theme", "surah_number", "aya_from", "aya_to", "keywords"],
        key=aya_key,
    )
    return AyaTopicsSchema(
        topics=sorted((_summary(r) for r in topics), key=lambda x: x.name.lower()),
        themes=[ThemeSchema(**{**r, "keywords": _scalar(r["keywords"]) or ""}) for r in themes],
    )


@router.get("/themes/{surah_number}")
def get_surah_themes(surah_number: int, g: Graph = Depends(graph)) -> list[ThemeSchema]:
    """The themes of a surah in aya order."""
    rows = g.cypher(
        "MATCH (th:Theme {surah_number: $n}) "
        "RETURN th.id, th.theme, th.surah_number, th.aya_from, th.aya_to, th.keywords",
        columns=["id", "theme", "surah_number", "aya_from", "aya_to", "keywords"],
        n=surah_number,
    )
    themes = [ThemeSchema(**{**r, "keywords": _scalar(r["keywords"]) or ""}) for r in rows]
    themes.sort(key=lambda t: (t.aya_from, t.aya_to))
    return themes


@router.get("/topics/for-ayas")
def topics_for_ayas(keys: str = Query(...), g: Graph = Depends(graph)) -> dict[str, list[str]]:
    """Topic names per aya for a comma separated list of aya keys (used for chips)."""
    aya_keys = [k for k in keys.split(",") if k]
    rows = g.cypher(
        "MATCH (a:Aya)-[:HAS_TOPIC]->(t:Topic) WHERE a.id IN $keys RETURN a.id, t.name",
        columns=["aya_key", "name"],
        keys=aya_keys,
    )
    result: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        result[r["aya_key"]].append(r["name"])
    return {k: sorted(v) for k, v in result.items()}
