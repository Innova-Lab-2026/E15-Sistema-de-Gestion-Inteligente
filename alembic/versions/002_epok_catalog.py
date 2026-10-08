"""Add epok category fields to activity_categories

Revision ID: 002_epok_catalog
Revises: 001_initial_catalog
Create Date: 2026-09-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_epok_catalog"
down_revision: Union[str, None] = "001_initial_catalog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "activity_categories",
        sa.Column("epok_category_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "activity_categories",
        sa.Column("epok_category_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("activity_categories", "epok_category_name")
    op.drop_column("activity_categories", "epok_category_id")
