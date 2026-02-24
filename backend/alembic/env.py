from alembic import context
from sqlalchemy import engine_from_config, pool

from quranref.settings import get_settings
from quranref.sql_models import Base

target_metadata = Base.metadata


def _sa_dsn() -> str:
    """Return the SQLAlchemy-compatible DSN using the psycopg (v3) driver."""
    dsn = get_settings().db_dsn
    if dsn.startswith("postgresql://"):
        dsn = "postgresql+psycopg://" + dsn[len("postgresql://"):]
    return dsn


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emit SQL to stdout."""
    context.configure(
        url=_sa_dsn(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connect to the database."""
    configuration = {"sqlalchemy.url": _sa_dsn()}
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
