"""Add tafsir tables.

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tafsir_resources",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String, nullable=False, unique=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("language", sa.String, nullable=False),
        sa.Column("author", sa.String, nullable=False, server_default=""),
        sa.Column("source", sa.String, nullable=False, server_default=""),
        sa.Column("license", sa.String, nullable=False, server_default=""),
    )
    op.create_table(
        "tafsir_texts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "resource_id",
            sa.Integer,
            sa.ForeignKey("tafsir_resources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_key", sa.String, nullable=False),
        sa.Column("to_key", sa.String, nullable=False),
        sa.Column("aya_keys", JSONB, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
    )
    op.create_index("idx_tafsir_texts_resource", "tafsir_texts", ["resource_id"])
    op.create_table(
        "tafsir_entries",
        sa.Column(
            "resource_id",
            sa.Integer,
            sa.ForeignKey("tafsir_resources.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("aya_key", sa.String, primary_key=True),
        sa.Column(
            "text_id",
            sa.Integer,
            sa.ForeignKey("tafsir_texts.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("tafsir_entries")
    op.drop_index("idx_tafsir_texts_resource", table_name="tafsir_texts")
    op.drop_table("tafsir_texts")
    op.drop_table("tafsir_resources")
