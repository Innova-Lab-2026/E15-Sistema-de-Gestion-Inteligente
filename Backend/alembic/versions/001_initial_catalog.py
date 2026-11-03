"""Initial catalog schema

Revision ID: 001_initial_catalog
Revises:
Create Date: 2026-09-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_catalog"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activity_categories",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("example", sa.String(length=255), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(
        op.f("ix_activity_categories_code"),
        "activity_categories",
        ["code"],
        unique=False,
    )

    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("jurisdiction", sa.String(length=64), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("validity_status", sa.String(length=32), nullable=False),
        sa.Column("transform_rule", sa.String(length=255), nullable=True),
        sa.Column("backup_url", sa.String(length=512), nullable=True),
        sa.Column(
            "related_activities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "map_layers",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("layer_type", sa.String(length=64), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "requirements",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("documents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("activity_id", sa.String(length=64), nullable=False),
        sa.Column("commune", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activity_categories.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_requirements_activity_id"),
        "requirements",
        ["activity_id"],
        unique=False,
    )

    op.create_table(
        "offices",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("address", sa.String(length=512), nullable=False),
        sa.Column("opening_hours", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("commune", sa.String(length=64), nullable=True),
        sa.Column("neighborhood", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "requirement_sources",
        sa.Column("requirement_id", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["requirement_id"], ["requirements.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("requirement_id", "source_id"),
        sa.UniqueConstraint("requirement_id", "source_id"),
    )

    op.create_table(
        "office_sources",
        sa.Column("office_id", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["office_id"], ["offices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("office_id", "source_id"),
        sa.UniqueConstraint("office_id", "source_id"),
    )

    op.create_table(
        "office_activities",
        sa.Column("office_id", sa.String(length=64), nullable=False),
        sa.Column("activity_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["office_id"], ["offices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["activity_categories.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("office_id", "activity_id"),
        sa.UniqueConstraint("office_id", "activity_id"),
    )

    op.create_table(
        "map_layer_sources",
        sa.Column("map_layer_id", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["map_layer_id"], ["map_layers.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("map_layer_id", "source_id"),
        sa.UniqueConstraint("map_layer_id", "source_id"),
    )


def downgrade() -> None:
    op.drop_table("map_layer_sources")
    op.drop_table("office_activities")
    op.drop_table("office_sources")
    op.drop_table("requirement_sources")
    op.drop_table("offices")
    op.drop_index(op.f("ix_requirements_activity_id"), table_name="requirements")
    op.drop_table("requirements")
    op.drop_table("map_layers")
    op.drop_table("sources")
    op.drop_index(
        op.f("ix_activity_categories_code"), table_name="activity_categories"
    )
    op.drop_table("activity_categories")
