"""Import per-word meanings (glosses) onto Token vertices."""

import json
from pathlib import Path

from age_orm import Database, Graph

from .db import GRAPH_NAME


def load_gloss_file(path: Path) -> dict[str, str]:
    """Read a word-by-word translation file.

    Accepts the QUL export format, a JSON object mapping "surah:aya:word" to the
    meaning, or a JSON list of objects with ``surah``/``ayah``/``word`` (or
    ``location``) and ``text`` keys.
    """
    with open(path, encoding="utf-8") as fp:
        data = json.load(fp)
    if isinstance(data, dict):
        return {str(k): str(v) for k, v in data.items() if v}
    result: dict[str, str] = {}
    for rec in data:
        text = rec.get("text") or rec.get("translation")
        if not text:
            continue
        location = rec.get("location") or f"{rec['surah']}:{rec['ayah']}:{rec['word']}"
        result[str(location)] = str(text)
    return result


def _has_jsonb_cast(db: Database) -> bool:
    """AGE 1.8 added casts between agtype and jsonb; older versions lack them."""
    with db._pool.connection() as conn:
        try:
            conn.execute("SELECT ('{}'::agtype)::jsonb, ('{}'::jsonb)::agtype")
            return True
        except Exception:
            conn.rollback()
            return False


def _import_with_sql(db: Database, language: str, glosses: dict[str, str]) -> int:
    """One UPDATE over the Token table, merging the language into each glosses map."""
    ids = list(glosses)
    texts = [glosses[i].strip() for i in ids]
    with db._pool.connection() as conn:
        cur = conn.execute(
            f'UPDATE {GRAPH_NAME}."Token" AS t '
            "SET properties = ((t.properties::jsonb) || jsonb_build_object("
            "  'glosses', COALESCE((t.properties::jsonb)->'glosses', '{}'::jsonb)"
            "  || jsonb_build_object(%(language)s::text, g.text)))::agtype "
            "FROM unnest(%(ids)s::text[], %(texts)s::text[]) AS g(id, text) "
            "WHERE ((t.properties::jsonb)->>'id') = g.id",
            {"language": language, "ids": ids, "texts": texts},
        )
        updated = cur.rowcount
        conn.commit()
    return updated


def _import_with_cypher(g: Graph, language: str, glosses: dict[str, str]) -> int:
    """One indexed Cypher update per token (works on any AGE version).

    A batched UNWIND cannot use an index on the unwound variable, so this is the
    fastest portable form; it needs the GIN index that db init creates.
    """
    existing = {
        r["id"]: (r["glosses"] or {})
        for r in g.cypher("MATCH (t:Token) RETURN t.id, t.glosses", columns=["id", "glosses"])
    }
    updated = 0
    for token_id, gloss in glosses.items():
        if token_id not in existing:
            continue
        merged = dict(existing[token_id])
        merged[language] = gloss.strip()
        g.cypher("MATCH (t:Token {id: $id}) SET t.glosses = $glosses", id=token_id, glosses=merged)
        updated += 1
    return updated


def import_word_glosses(g: Graph, db: Database, language: str, glosses: dict[str, str]) -> int:
    """Set ``glosses[language]`` on every Token named in ``glosses``.

    Existing glosses in other languages are kept. Entries whose location is not a
    token (for example aya-end markers) are ignored. Returns the number of tokens
    updated.
    """
    if _has_jsonb_cast(db):
        return _import_with_sql(db, language, glosses)
    return _import_with_cypher(g, language, glosses)
