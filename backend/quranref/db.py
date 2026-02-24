from collections.abc import Generator

from age_orm import Database, Graph
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import get_settings

GRAPH_NAME = "quran_graph"

_db: Database | None = None
_engine = None
_session_factory = None


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


def _sa_dsn() -> str:
    """Return the SQLAlchemy-compatible DSN using the psycopg (v3) driver."""
    settings = get_settings()
    # Replace postgresql:// with postgresql+psycopg:// for psycopg v3
    dsn = settings.db_dsn
    if dsn.startswith("postgresql://"):
        dsn = "postgresql+psycopg://" + dsn[len("postgresql://"):]
    return dsn


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_sa_dsn())
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a SQLAlchemy session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
