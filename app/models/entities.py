from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActivityCategory(Base):
    __tablename__ = "activity_categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    example: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    epok_category_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    epok_category_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    epok_rubro_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, unique=True, index=True
    )

    requirements: Mapped[list["Requirement"]] = relationship(back_populates="activity")
    offices: Mapped[list["Office"]] = relationship(
        secondary="office_activities",
        back_populates="activities",
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    organization: Mapped[str] = mapped_column(String(255))
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    source_type: Mapped[str] = mapped_column(String(64))
    jurisdiction: Mapped[str] = mapped_column(String(64), default="CABA")
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    validity_status: Mapped[str] = mapped_column(String(32), default="available")
    transform_rule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    backup_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    related_activities: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="available")
    documents: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    steps: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    activity_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("activity_categories.id", ondelete="CASCADE"),
        index=True,
    )
    commune: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    activity: Mapped[ActivityCategory] = relationship(back_populates="requirements")
    sources: Mapped[list[Source]] = relationship(secondary="requirement_sources")


class Office(Base):
    __tablename__ = "offices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    organization: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(64), default="physical_office")
    address: Mapped[str] = mapped_column(String(512))
    opening_hours: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    commune: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="available")

    activities: Mapped[list[ActivityCategory]] = relationship(
        secondary="office_activities",
        back_populates="offices",
    )
    sources: Mapped[list[Source]] = relationship(secondary="office_sources")


class MapLayer(Base):
    __tablename__ = "map_layers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    layer_type: Mapped[str] = mapped_column(String(64), default="geojson")
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="available")

    sources: Mapped[list[Source]] = relationship(secondary="map_layer_sources")


class RequirementSource(Base):
    __tablename__ = "requirement_sources"
    __table_args__ = (UniqueConstraint("requirement_id", "source_id"),)

    requirement_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("requirements.id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    )


class OfficeSource(Base):
    __tablename__ = "office_sources"
    __table_args__ = (UniqueConstraint("office_id", "source_id"),)

    office_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("offices.id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    )


class OfficeActivity(Base):
    __tablename__ = "office_activities"
    __table_args__ = (UniqueConstraint("office_id", "activity_id"),)

    office_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("offices.id", ondelete="CASCADE"),
        primary_key=True,
    )
    activity_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("activity_categories.id", ondelete="CASCADE"),
        primary_key=True,
    )


class MapLayerSource(Base):
    __tablename__ = "map_layer_sources"
    __table_args__ = (UniqueConstraint("map_layer_id", "source_id"),)

    map_layer_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("map_layers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    )
