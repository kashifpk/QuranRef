"""Initial schema: users and meta_info tables.

Revision ID: 0001
Revises:
Create Date: 2026-02-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("google_id", sa.String, unique=True, nullable=False),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("name", sa.String, nullable=False, server_default=""),
        sa.Column("picture_url", sa.String, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("last_login", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        if_not_exists=True,
    )
    op.create_table(
        "meta_info",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("value", JSONB, nullable=False),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("meta_info")
    op.drop_table("users")
