"""Import per-word meanings (glosses) onto Token vertices."""

import json
from pathlib import Path

from age_orm import Graph


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


def import_word_glosses(
    g: Graph, language: str, glosses: dict[str, str], batch_size: int = 500
) -> int:
    """Set ``glosses[language]`` on every Token named in ``glosses``.

    Existing glosses in other languages are kept. Returns the number of tokens updated.
    """
    existing = {
        r["id"]: (r["glosses"] or {})
        for r in g.cypher("MATCH (t:Token) RETURN t.id, t.glosses", columns=["id", "glosses"])
    }
    rows = []
    for token_id, gloss in glosses.items():
        if token_id not in existing:
            continue
        merged = dict(existing[token_id])
        merged[language] = gloss.strip()
        rows.append({"id": token_id, "glosses": merged})

    for start in range(0, len(rows), batch_size):
        g.cypher(
            "UNWIND $rows AS r MATCH (t:Token {id: r.id}) SET t.glosses = r.glosses",
            rows=rows[start : start + batch_size],
        )
    return len(rows)
