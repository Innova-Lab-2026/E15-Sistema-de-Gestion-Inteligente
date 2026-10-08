"""Add epok_rubro_id to activity_categories

Revision ID: 003_epok_rubro_id
Revises: 002_epok_catalog
Create Date: 2026-09-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_epok_rubro_id"
down_revision: Union[str, None] = "002_epok_catalog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "activity_categories",
        sa.Column("epok_rubro_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_activity_categories_epok_rubro_id",
        "activity_categories",
        ["epok_rubro_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_activity_categories_epok_rubro_id", table_name="activity_categories")
    op.drop_column("activity_categories", "epok_rubro_id")
