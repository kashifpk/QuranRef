"""Add surah_info table.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "surah_info",
        sa.Column("surah_number", sa.Integer, primary_key=True),
        sa.Column("language", sa.String, primary_key=True),
        sa.Column("text", sa.Text, nullable=False, server_default=""),
        sa.Column("short_text", sa.Text, nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_table("surah_info")
