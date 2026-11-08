"""Log of activities the system did not recognize (B16)

Revision ID: 005_unrecognized_activities
Revises: 004_source_license
Create Date: 2026-11-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_unrecognized_activities"
down_revision: Union[str, None] = "004_source_license"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "unrecognized_activities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("raw_text", sa.String(length=255), nullable=False),
        sa.Column("candidates", postgresql.JSONB(), nullable=True),
        sa.Column("chosen_code", sa.String(length=64), nullable=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("provider", sa.String(length=16), nullable=False),
    )
    op.create_index("ix_unrecognized_activities_conversation_id", "unrecognized_activities", ["conversation_id"])


def downgrade() -> None:
    op.drop_index("ix_unrecognized_activities_conversation_id", table_name="unrecognized_activities")
    op.drop_table("unrecognized_activities")
