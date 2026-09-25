"""Bulk property updates on existing vertices."""

import json

from age_orm import Database, Graph

from .db import GRAPH_NAME


def _has_jsonb_cast(db: Database) -> bool:
    with db._pool.connection() as conn:
        try:
            conn.execute("SELECT ('{}'::agtype)::jsonb, ('{}'::jsonb)::agtype")
            return True
        except Exception:
            conn.rollback()
            return False


def set_vertex_properties(g: Graph, db: Database, label: str, updates: dict[str, dict]) -> int:
    """Merge ``updates[id]`` into the properties of each vertex of ``label`` with that id.

    Uses one SQL statement with the agtype/jsonb casts of AGE 1.8; on older AGE it
    falls back to one Cypher SET per vertex (which needs the GIN property index).
    Returns the number of vertices updated.
    """
    if not updates:
        return 0
    if _has_jsonb_cast(db):
        ids = list(updates)
        payloads = [json.dumps(updates[i], ensure_ascii=False) for i in ids]
        with db._pool.connection() as conn:
            cur = conn.execute(
                f'UPDATE {GRAPH_NAME}."{label}" AS v '
                "SET properties = ((v.properties::jsonb) || u.props::jsonb)::agtype "
                "FROM unnest(%(ids)s::text[], %(props)s::text[]) AS u(id, props) "
                "WHERE ((v.properties::jsonb)->>'id') = u.id",
                {"ids": ids, "props": payloads},
            )
            updated = cur.rowcount
            conn.commit()
        return updated

    updated = 0
    for vertex_id, props in updates.items():
        assignments = ", ".join(f"n.{key} = ${key}" for key in props)
        g.cypher(f"MATCH (n:{label} {{id: $id}}) SET {assignments}", id=vertex_id, **props)
        updated += 1
    return updated
