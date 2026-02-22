from age_orm import Database, Graph

from .settings import get_settings

GRAPH_NAME = "quran_graph"

_db: Database | None = None


def get_db() -> Database:
    global _db
    if _db is None:
        settings = get_settings()
        _db = Database(settings.db_dsn)
    return _db


def graph() -> Graph:
    db = get_db()
    return db.graph(GRAPH_NAME)


def raw_connection():
    db = get_db()
    return db._pool.connection()
