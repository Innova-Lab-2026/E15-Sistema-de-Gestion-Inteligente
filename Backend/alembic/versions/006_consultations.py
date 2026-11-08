"""Store every consultation (B20, traceability in arquitectura-ia.md §16)

Revision ID: 006_consultations
Revises: 005_unrecognized_activities
Create Date: 2026-11-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006_consultations"
down_revision: Union[str, None] = "005_unrecognized_activities"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "consultations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("request", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=True),
        sa.Column("interpretation", postgresql.JSONB(), nullable=True),
        sa.Column("location", postgresql.JSONB(), nullable=True),
        sa.Column("source_ids", postgresql.JSONB(), nullable=True),
        sa.Column("provider", sa.String(length=16), nullable=True),
        sa.Column("llm_model", sa.String(length=128), nullable=True),
        sa.Column("prompt_version", sa.String(length=32), nullable=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("response", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_consultations_conversation_id", "consultations", ["conversation_id"])
    op.create_index("ix_consultations_created_at", "consultations", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_consultations_created_at", table_name="consultations")
    op.drop_index("ix_consultations_conversation_id", table_name="consultations")
    op.drop_table("consultations")
