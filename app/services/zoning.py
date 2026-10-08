"""Servicio de zonificacion / normativa por lote (epok)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import ActivityCategory
from app.providers.epok import ZoningResult, get_epok_client
from app.schemas.zoning import ParcelOut, ZoningOut, ZoningRequest


class ZoningService:
    def __init__(self, settings: Settings, db: AsyncSession | None = None) -> None:
        self.settings = settings
        self.db = db
        self.client = get_epok_client(settings)

    async def lookup(self, body: ZoningRequest) -> ZoningOut:
        category_id = body.epok_category_id
        rubro_id = body.epok_rubro_id

        if body.activity_code and self.db is not None:
            activity = await self.db.scalar(
                select(ActivityCategory).where(
                    ActivityCategory.code == body.activity_code,
                    ActivityCategory.enabled.is_(True),
                )
            )
            if activity is not None:
                category_id = category_id or activity.epok_category_id
                rubro_id = rubro_id or activity.epok_rubro_id

        result = await self.client.lookup_zoning(
            latitude=body.latitude,
            longitude=body.longitude,
            epok_category_id=category_id,
            epok_rubro_id=rubro_id,
        )
        return self.to_schema(result)

    @staticmethod
    def to_schema(result: ZoningResult) -> ZoningOut:
        parcel = None
        if result.parcel is not None:
            parcel = ParcelOut(
                smp=result.parcel.smp,
                direccion=result.parcel.direccion,
                seccion=result.parcel.seccion,
                manzana=result.parcel.manzana,
                parcela=result.parcel.parcela,
                superficie_total=result.parcel.superficie_total,
                centroide=result.parcel.centroide,
            )
        return ZoningOut(
            status=result.status,
            latitude=result.latitude,
            longitude=result.longitude,
            parcel=parcel,
            mixtura=result.mixtura,
            usos=result.usos,
            affectations=result.affectations,
            epok_category_id=result.epok_category_id,
            epok_rubro_id=result.epok_rubro_id,
            rubro_allowed=result.rubro_allowed,
            allowed_rubro_ids_sample=result.allowed_rubro_ids,
            referencias=result.referencias,
            message=result.message,
            provider_id=result.provider_id,
            provider_name=result.provider_name,
            retrieved_at=result.retrieved_at.isoformat(),
        )
