"""Add collections and collection_items tables.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "collections",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "name", name="uq_collections_user_name"),
    )
    op.create_index("idx_collections_user_id", "collections", ["user_id"])
    op.create_table(
        "collection_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "collection_id",
            sa.Integer,
            sa.ForeignKey("collections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("aya_key", sa.String, nullable=False),
        sa.Column("note", sa.Text, nullable=False, server_default=""),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("collection_id", "aya_key", name="uq_collection_items_aya"),
    )
    op.create_index("idx_collection_items_collection_id", "collection_items", ["collection_id"])


def downgrade() -> None:
    op.drop_index("idx_collection_items_collection_id", table_name="collection_items")
    op.drop_table("collection_items")
    op.drop_index("idx_collections_user_id", table_name="collections")
    op.drop_table("collections")
