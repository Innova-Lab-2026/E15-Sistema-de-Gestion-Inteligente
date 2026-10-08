"""Esquemas de zonificacion Ciudad 3D / epok."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ZoningRequest(BaseModel):
    latitude: float = Field(examples=[-34.604])
    longitude: float = Field(examples=[-58.413])
    activity_code: Optional[str] = Field(
        default=None, examples=["rubro_102", "rubro_309"]
    )
    epok_category_id: Optional[int] = Field(default=None, examples=[1])
    epok_rubro_id: Optional[int] = Field(default=None, examples=[102])


class ParcelOut(BaseModel):
    smp: str
    direccion: Optional[str] = None
    seccion: Optional[str] = None
    manzana: Optional[str] = None
    parcela: Optional[str] = None
    superficie_total: Optional[str] = None
    centroide: Optional[list[float]] = None


class ZoningOut(BaseModel):
    status: Literal[
        "ok",
        "parcel_not_found",
        "unavailable",
        "rubro_allowed",
        "rubro_not_allowed",
    ]
    latitude: float
    longitude: float
    parcel: Optional[ParcelOut] = None
    mixtura: Optional[int] = None
    usos: list[int] = Field(default_factory=list)
    affectations: Optional[dict[str, Any]] = None
    epok_category_id: Optional[int] = None
    epok_rubro_id: Optional[int] = None
    rubro_allowed: Optional[bool] = None
    allowed_rubro_ids_sample: list[int] = Field(default_factory=list)
    referencias: Optional[dict[str, Any]] = None
    message: Optional[str] = None
    provider_id: str
    provider_name: str
    retrieved_at: str
    source_ids: list[str] = Field(default_factory=lambda: ["source-004"])
