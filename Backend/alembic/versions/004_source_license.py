"""Add license to sources (data/*.meta.json)

Revision ID: 004_source_license
Revises: 003_epok_rubro_id
Create Date: 2026-11-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_source_license"
down_revision: Union[str, None] = "003_epok_rubro_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sources", sa.Column("license", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("sources", "license")
