"""Add aya_search table for normalized full text search.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm SCHEMA public")
    op.create_table(
        "aya_search",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("aya_key", sa.String, nullable=False),
        sa.Column("language", sa.String, nullable=False),
        sa.Column("text_type", sa.String, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("text_norm", sa.Text, nullable=False),
        sa.UniqueConstraint("aya_key", "language", "text_type", name="uq_aya_search_key"),
    )
    op.create_index("idx_aya_search_lang_type", "aya_search", ["language", "text_type"])
    op.create_index(
        "idx_aya_search_norm_trgm",
        "aya_search",
        ["text_norm"],
        postgresql_using="gin",
        postgresql_ops={"text_norm": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("idx_aya_search_norm_trgm", table_name="aya_search")
    op.drop_index("idx_aya_search_lang_type", table_name="aya_search")
    op.drop_table("aya_search")
