from __future__ import annotations

import math
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.models import ActivityCategory, MapLayer, Office, Requirement, Source
from app.schemas.consultation import (
    ConsultationActivity,
    ConsultationInterpretation,
    ConsultationLocation,
    ConsultationRequest,
    ConsultationResponse,
    DataStatus,
    DocumentItem,
    MapLayerItem,
    OfficeItem,
    RequirementItem,
    SourceItem,
    StepItem,
    TerritorialItem,
)
from app.services.interpretation import InterpretationService
from app.services.location import LocationService
from app.services.zoning import ZoningService
from app.schemas.zoning import ZoningOut
from app.providers.epok import get_epok_client
from app.db.ba_data_context import gastronomy_context


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class ConsultationService:
    def __init__(self, settings: Settings, db: AsyncSession) -> None:
        self.settings = settings
        self.db = db
        self.location_service = LocationService(settings)

    async def create(self, body: ConsultationRequest) -> ConsultationResponse:
        activity_code = body.activity_code
        address = body.address
        original_query = body.query
        confidence = 1.0
        activity_raw: str | None = None

        # Natural language path
        if body.query and (not activity_code or not address):
            interpreted = await InterpretationService(
                self.settings, self.db
            ).interpret(body.query.strip())

            original_query = interpreted.original_query
            if interpreted.status in {"needs_clarification", "activity_unknown", "out_of_scope"}:
                return ConsultationResponse(
                    status=(
                        "activity_unknown"
                        if interpreted.status == "activity_unknown"
                        else "out_of_scope"
                        if interpreted.status == "out_of_scope"
                        else "needs_clarification"
                    ),
                    interpretation=None,
                    location=ConsultationLocation(
                        status="pending",
                        message=interpreted.clarification_question,
                    ),
                    summary=interpreted.clarification_question
                    or "Se necesita aclaracion para continuar.",
                    data_status=DataStatus(
                        overall="blocked",
                        missing=list(interpreted.missing_fields),
                    ),
                    message=interpreted.clarification_question,
                )

            activity_code = interpreted.activity.normalized_category
            address = interpreted.location.address or interpreted.location.raw_text
            confidence = interpreted.activity.confidence
            activity_raw = interpreted.activity.raw_text

        if not activity_code:
            return ConsultationResponse(
                status="activity_unknown",
                location=ConsultationLocation(status="pending"),
                summary="No se indico una actividad del catalogo.",
                data_status=DataStatus(overall="blocked", missing=["activity"]),
            )

        activity = await self._get_activity(activity_code)
        if activity is None:
            return ConsultationResponse(
                status="activity_unknown",
                location=ConsultationLocation(status="pending"),
                summary=(
                    f'La actividad "{activity_code}" no pertenece al catalogo del MVP.'
                ),
                data_status=DataStatus(overall="blocked", missing=["activity"]),
                message="activity_out_of_scope",
            )

        interpretation = ConsultationInterpretation(
            intent="start_commercial_activity",
            activity=ConsultationActivity(
                normalized_category=activity.code,
                display_name=activity.name,
                confidence=confidence,
                raw_text=activity_raw,
            ),
            original_query=original_query
            or f"Consulta deterministica: {activity.code} en {address or 'ubicacion confirmada'}",
        )

        # Location resolution
        if body.confirmed_location is not None:
            loc = body.confirmed_location
            location = ConsultationLocation(
                normalized_address=loc.normalized_address,
                commune=loc.commune,
                neighborhood=loc.neighborhood,
                city=loc.city,
                latitude=loc.latitude,
                longitude=loc.longitude,
                precision=loc.precision,
                status="confirmed",
            )
        else:
            if not address:
                return ConsultationResponse(
                    status="needs_clarification",
                    interpretation=interpretation,
                    location=ConsultationLocation(status="pending"),
                    summary="Falta una direccion para geocodificar.",
                    data_status=DataStatus(overall="blocked", missing=["location"]),
                )
            geo = await self.location_service.geocode(address)
            if geo.status == "ambiguous":
                return ConsultationResponse(
                    status="needs_location_confirmation",
                    interpretation=interpretation,
                    location=ConsultationLocation(
                        status="ambiguous",
                        candidates=geo.candidates,
                        message=geo.message,
                    ),
                    summary=(
                        "Hay varias coincidencias de ubicacion. "
                        "Confirma una con confirmed_location para continuar."
                    ),
                    data_status=DataStatus(
                        overall="blocked",
                        missing=["confirmed_location"],
                        warnings=["ambiguous_address"],
                    ),
                    message=geo.message,
                )
            if geo.status == "out_of_scope":
                return ConsultationResponse(
                    status="out_of_scope",
                    interpretation=interpretation,
                    location=ConsultationLocation(
                        status="out_of_scope",
                        message=geo.message,
                        candidates=geo.candidates,
                    ),
                    summary=geo.message or "La ubicacion esta fuera de CABA.",
                    data_status=DataStatus(
                        overall="blocked", missing=["location_in_caba"]
                    ),
                    message=geo.message,
                )
            if geo.status == "not_found":
                return ConsultationResponse(
                    status="location_not_found",
                    interpretation=interpretation,
                    location=ConsultationLocation(
                        status="not_found",
                        message=geo.message,
                    ),
                    summary=geo.message or "No se pudo geocodificar la direccion.",
                    data_status=DataStatus(overall="blocked", missing=["location"]),
                    message=geo.message,
                )
            location = ConsultationLocation(
                normalized_address=geo.normalized_address,
                commune=geo.commune,
                neighborhood=geo.neighborhood,
                city=geo.city,
                latitude=geo.latitude,
                longitude=geo.longitude,
                precision=geo.precision,
                status="confirmed",
                candidates=geo.candidates,
            )

        # Retrieve official-ish seed data
        payload = await self._retrieve(
            activity=activity,
            commune=location.commune,
            neighborhood=location.neighborhood,
            latitude=location.latitude,
            longitude=location.longitude,
        )

        zoning_out: ZoningOut | None = None
        missing: list[str] = []
        warnings: list[str] = []

        if location.latitude is not None and location.longitude is not None:
            zoning_result = await get_epok_client(self.settings).lookup_zoning(
                latitude=location.latitude,
                longitude=location.longitude,
                epok_category_id=activity.epok_category_id,
                epok_rubro_id=activity.epok_rubro_id,
            )
            zoning_out = ZoningService.to_schema(zoning_result)
            if zoning_result.status == "unavailable":
                missing.append("zoning_epok")
                warnings.append("epok_unavailable")
            elif zoning_result.status == "parcel_not_found":
                missing.append("parcel_smp")
                warnings.append("epok_parcel_not_found")
            elif zoning_result.rubro_allowed is False:
                warnings.append("rubro_not_allowed_in_mixtura")
            # Enrich territorial block with smp/mixtura
            if zoning_result.parcel is not None:
                payload["territorial_information"].insert(
                    0,
                    TerritorialItem(
                        title="Normativa Ciudad 3D / epok",
                        description=(
                            f"SMP {zoning_result.parcel.smp}"
                            f" ({zoning_result.parcel.direccion or 'sin direccion catastral'}). "
                            f"Mixtura: {zoning_result.mixtura or 'N/D'}. "
                            f"Rubro {activity.epok_rubro_id} ({activity.name}): "
                            f"{zoning_result.message or zoning_result.status}."
                        ),
                        source_ids=["source-004"],
                    ),
                )
                # Ensure epok source appears in sources list
                if "source-004" not in {
                    s.id for s in payload["sources"]
                }:
                    epok_src = await self.db.get(Source, "source-004")
                    if epok_src is not None:
                        payload["sources"].append(
                            SourceItem(
                                id=epok_src.id,
                                name=epok_src.name,
                                organization=epok_src.organization,
                                url=epok_src.url,
                                source_type=epok_src.source_type,
                                validity_status=epok_src.validity_status,
                                ingested_at=epok_src.ingested_at.isoformat()
                                if epok_src.ingested_at
                                else None,
                            )
                        )

        if not payload["requirements"]:
            missing.append("requirements")
        if not payload["physical_offices"] and not payload["online_procedures"]:
            missing.append("offices")
        if not payload["sources"]:
            missing.append("sources")
            warnings.append("no_sources_linked")

        overall = "complete" if not missing else "partial"
        status = "complete" if overall == "complete" else "partial"

        zoning_bit = ""
        if zoning_out is not None and zoning_out.parcel is not None:
            if zoning_out.rubro_allowed is True:
                rubro_txt = "permitido"
            elif zoning_out.rubro_allowed is False:
                rubro_txt = "no permitido"
            else:
                rubro_txt = "sin check de rubro"
            zoning_bit = (
                f" Parcela SMP {zoning_out.parcel.smp}, mixtura {zoning_out.mixtura}; "
                f"rubro epok {activity.epok_rubro_id}: {rubro_txt}."
            )

        summary = (
            f"Orientacion para {activity.name} en "
            f"{location.normalized_address or 'la ubicacion consultada'} "
            f"({location.neighborhood or 'barrio N/D'}, {location.commune or 'comuna N/D'})."
            f"{zoning_bit} "
            f"Se recuperaron {len(payload['requirements'])} requisito(s) y "
            f"{len(payload['physical_offices']) + len(payload['online_procedures'])} canal(es) "
            "desde el catalogo integrado (seed MVP). "
            "Validar siempre contra las fuentes citadas."
        )

        return ConsultationResponse(
            status=status,  # type: ignore[arg-type]
            interpretation=interpretation,
            location=location,
            summary=summary,
            requirements=payload["requirements"],
            documents=payload["documents"],
            steps=payload["steps"],
            territorial_information=payload["territorial_information"],
            online_procedures=payload["online_procedures"],
            physical_offices=payload["physical_offices"],
            map_layers=payload["map_layers"],
            sources=payload["sources"],
            zoning=zoning_out,
            data_status=DataStatus(
                overall=overall,  # type: ignore[arg-type]
                missing=missing,
                warnings=warnings,
            ),
        )

    async def _get_activity(self, code: str) -> ActivityCategory | None:
        return await self.db.scalar(
            select(ActivityCategory).where(
                ActivityCategory.code == code,
                ActivityCategory.enabled.is_(True),
            )
        )

    async def _retrieve(
        self,
        *,
        activity: ActivityCategory,
        commune: str | None,
        neighborhood: str | None = None,
        latitude: float | None,
        longitude: float | None,
    ) -> dict[str, Any]:
        req_rows = list(
            await self.db.scalars(
                select(Requirement)
                .where(Requirement.activity_id == activity.id)
                .options(selectinload(Requirement.sources))
                .order_by(Requirement.id)
            )
        )
        # commune filter: keep null (city-wide) or matching commune
        if commune:
            req_rows = [
                r
                for r in req_rows
                if r.commune is None or r.commune.lower() == commune.lower()
            ]

        offices = list(
            await self.db.scalars(
                select(Office)
                .options(selectinload(Office.sources), selectinload(Office.activities))
                .order_by(Office.id)
            )
        )
        offices = [o for o in offices if any(a.id == activity.id for a in o.activities)]
        if commune:
            offices = [
                o
                for o in offices
                if o.commune is None or o.commune.lower() == commune.lower()
            ]

        layers = list(
            await self.db.scalars(
                select(MapLayer)
                .options(selectinload(MapLayer.sources))
                .order_by(MapLayer.id)
            )
        )

        requirements: list[RequirementItem] = []
        documents: list[DocumentItem] = []
        steps: list[StepItem] = []
        source_ids: set[str] = set()

        for req in req_rows:
            sids = [s.id for s in req.sources]
            source_ids.update(sids)
            docs = [
                DocumentItem(
                    name=d.get("name", "Documento"),
                    details=d.get("details"),
                    url_fuente=d.get("url_fuente") or d.get("url_fuente_expres"),
                    source_ids=sids,
                )
                for d in (req.documents or [])
                if isinstance(d, dict)
            ]
            stps = [
                StepItem(
                    order=int(s.get("order", 0)),
                    title=s.get("title", "Paso"),
                    description=s.get("description"),
                    url_fuente=s.get("url_fuente") or s.get("url_fuente_expres"),
                    source_ids=sids,
                )
                for s in (req.steps or [])
                if isinstance(s, dict)
            ]
            documents.extend(docs)
            steps.extend(stps)
            requirements.append(
                RequirementItem(
                    id=req.id,
                    title=req.title,
                    description=req.description,
                    status=req.status,
                    documents=docs,
                    steps=stps,
                    source_ids=sids,
                )
            )

        physical: list[OfficeItem] = []
        online: list[OfficeItem] = []
        for office in offices:
            sids = [s.id for s in office.sources]
            source_ids.update(sids)
            distance = None
            if latitude is not None and longitude is not None:
                distance = round(
                    _haversine_m(latitude, longitude, office.latitude, office.longitude),
                    1,
                )
            item = OfficeItem(
                id=office.id,
                name=office.name,
                organization=office.organization,
                type=office.type,
                address=office.address,
                opening_hours=office.opening_hours,
                url=office.url,
                latitude=office.latitude,
                longitude=office.longitude,
                commune=office.commune,
                neighborhood=office.neighborhood,
                distance_meters=distance,
                status=office.status,
                source_ids=sids,
            )
            if office.type == "online_channel":
                online.append(item)
            else:
                physical.append(item)

        map_layers: list[MapLayerItem] = []
        for layer in layers:
            sids = [s.id for s in layer.sources]
            source_ids.update(sids)
            map_layers.append(
                MapLayerItem(
                    id=layer.id,
                    name=layer.name,
                    description=layer.description,
                    layer_type=layer.layer_type,
                    url=layer.url,
                    status=layer.status,
                    source_ids=sids,
                )
            )

        territorial: list[TerritorialItem] = []
        if commune or latitude is not None:
            territorial.append(
                TerritorialItem(
                    title="Contexto territorial de la consulta",
                    description=(
                        f"Comuna: {commune or 'N/D'}. "
                        f"Barrio: {neighborhood or 'N/D'}. "
                        f"Coordenadas: ({latitude}, {longitude}). "
                        "Obtenido via geocodificacion USIG/mock."
                    ),
                    source_ids=["geocoder"],
                )
            )

        ba_ctx = gastronomy_context(commune=commune, neighborhood=neighborhood)
        if ba_ctx is not None:
            source_ids.add("source-002")
            parts = [
                f"Dataset BA Data oferta gastronomica: {ba_ctx.get('total_caba')} locales en CABA."
            ]
            if ba_ctx.get("count_comuna") is not None:
                parts.append(
                    f"Comuna {ba_ctx.get('comuna')}: {ba_ctx.get('count_comuna')} establecimientos."
                )
            if ba_ctx.get("count_barrio") is not None:
                parts.append(
                    f"Barrio {ba_ctx.get('barrio')}: {ba_ctx.get('count_barrio')} establecimientos."
                )
            cats = ba_ctx.get("by_categoria") or {}
            if cats:
                top = ", ".join(f"{k}={v}" for k, v in list(cats.items())[:4])
                parts.append(f"Categorias top CABA: {top}.")
            parts.append(f"Fuente: {ba_ctx.get('dataset_url')}.")
            territorial.append(
                TerritorialItem(
                    title="Contexto BA Data (oferta gastronomica)",
                    description=" ".join(parts),
                    source_ids=["source-002"],
                )
            )

        sources: list[SourceItem] = []
        if source_ids:
            # exclude synthetic geocoder id from DB lookup
            db_ids = [sid for sid in source_ids if sid != "geocoder"]
            if db_ids:
                rows = list(
                    await self.db.scalars(
                        select(Source).where(Source.id.in_(db_ids)).order_by(Source.id)
                    )
                )
                for src in rows:
                    sources.append(
                        SourceItem(
                            id=src.id,
                            name=src.name,
                            organization=src.organization,
                            url=src.url,
                            source_type=src.source_type,
                            validity_status=src.validity_status,
                            ingested_at=src.ingested_at.isoformat()
                            if src.ingested_at
                            else None,
                        )
                    )

        return {
            "requirements": requirements,
            "documents": documents,
            "steps": steps,
            "territorial_information": territorial,
            "online_procedures": online,
            "physical_offices": physical,
            "map_layers": map_layers,
            "sources": sources,
        }
