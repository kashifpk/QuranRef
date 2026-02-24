"""Add bookmarks table.

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("bookmark_type", sa.String, nullable=False),
        sa.Column("aya_key", sa.String, nullable=False),
        sa.Column("note", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "bookmark_type IN ('reading', 'note')", name="ck_bookmark_type"
        ),
    )
    op.create_index("idx_bookmarks_user_id", "bookmarks", ["user_id"])
    op.create_index(
        "uq_reading_bookmark",
        "bookmarks",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("bookmark_type = 'reading'"),
    )


def downgrade() -> None:
    op.drop_index("uq_reading_bookmark", table_name="bookmarks")
    op.drop_index("idx_bookmarks_user_id", table_name="bookmarks")
    op.drop_table("bookmarks")
