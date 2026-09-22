"""Build the aya_search table from the graph."""

from age_orm import Database, Graph

from .textnorm import normalize_for_search


def rebuild_search_index(g: Graph, db: Database, batch_size: int = 20_000) -> int:
    """Replace the contents of aya_search with every AYA_TEXT edge in the graph.

    Returns the number of rows written.
    """
    rows = g.cypher(
        "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) RETURN a.id, e.language, e.text_type, t.text",
        columns=["aya_key", "language", "text_type", "text"],
    )

    written = 0
    with db._pool.connection() as conn:
        conn.execute("TRUNCATE aya_search")
        with (
            conn.cursor() as cur,
            cur.copy(
                "COPY aya_search (aya_key, language, text_type, text, text_norm) FROM STDIN"
            ) as copy,
        ):
            for r in rows:
                text = r["text"] or ""
                copy.write_row(
                    (r["aya_key"], r["language"], r["text_type"], text, normalize_for_search(text))
                )
                written += 1
        conn.commit()
    return written
