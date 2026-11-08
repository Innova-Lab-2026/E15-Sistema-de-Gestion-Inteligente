from __future__ import annotations

import logging
import math
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.core.territory import normalize_commune, same_commune
from app.db.data_files import barrio, barrio_por_variante
from app.models import ActivityCategory, MapLayer, Office, Requirement, Source, UnrecognizedActivity
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
from app.schemas.interpretation import InterpretationResponse
from app.services.interpretation import InterpretationService
from app.services.messages import message_for
from app.services.location import LocationService
from app.services.zoning import ZoningService
from app.schemas.zoning import ZoningOut
from app.providers.epok import get_epok_client
from app.db.ba_data_context import gastronomy_context


logger = logging.getLogger(__name__)


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
        self._llm_fallback_reason: str | None = None

    async def create(self, body: ConsultationRequest) -> ConsultationResponse:
        response = await self._build_response(body)
        if self._llm_fallback_reason:
            # The LLM was configured but failed: the frontend can tell the user the
            # interpretation came from local rules.
            response.data_status.warnings.append("llm_fallback_mock")
        return response

    async def _build_response(self, body: ConsultationRequest) -> ConsultationResponse:
        activity_code = body.activity_code
        address = body.address
        original_query = body.query
        neighborhood_id = body.neighborhood_id
        approximate = False
        confidence = 1.0
        activity_raw: str | None = None
        interpreted: InterpretationResponse | None = None

        # Natural language path
        if body.query and (not activity_code or not address):
            interpreted = await InterpretationService(
                self.settings, self.db
            ).interpret(body.query.strip(), conversation_id=body.conversation_id)
            self._llm_fallback_reason = interpreted.fallback_reason

            original_query = interpreted.original_query
            # Activity + barrio without street: answer partially by barrio (B07).
            neighborhood_only = bool(
                interpreted.activity.normalized_category
                and not (interpreted.location.address or interpreted.location.raw_text)
                and interpreted.location.neighborhood_id
            )
            if (
                interpreted.status in {"needs_clarification", "activity_unknown", "out_of_scope"}
                and not neighborhood_only
            ):
                return ConsultationResponse(
                    status=(
                        "activity_unknown"
                        if interpreted.status == "activity_unknown"
                        else "out_of_scope"
                        if interpreted.status == "out_of_scope"
                        else "needs_clarification"
                    ),
                    # Partial interpretation: the Frontend keeps what was already understood.
                    interpretation=self._partial_interpretation(interpreted),
                    location=ConsultationLocation(status="pending"),
                    summary=interpreted.message or "Se necesita aclaracion para continuar.",
                    data_status=DataStatus(
                        overall="blocked",
                        missing=list(interpreted.missing_fields),
                    ),
                    reason=interpreted.reason,
                    message=interpreted.message,
                )

            activity_code = interpreted.activity.normalized_category
            address = interpreted.location.address or interpreted.location.raw_text
            neighborhood_id = neighborhood_id or interpreted.location.neighborhood_id
            approximate = interpreted.location.approximate
            confidence = interpreted.activity.confidence
            activity_raw = interpreted.activity.raw_text

        if not activity_code:
            return ConsultationResponse(
                status="activity_unknown",
                interpretation=self._partial_interpretation(interpreted),
                location=ConsultationLocation(status="pending"),
                summary=message_for("activity_missing"),
                data_status=DataStatus(overall="blocked", missing=["activity"]),
                reason="activity_missing",
                message=message_for("activity_missing"),
            )

        activity = await self._get_activity(activity_code)
        if activity is None:
            return ConsultationResponse(
                status="activity_unknown",
                interpretation=self._partial_interpretation(interpreted),
                location=ConsultationLocation(status="pending"),
                summary=message_for("activity_not_in_catalog"),
                data_status=DataStatus(overall="blocked", missing=["activity"]),
                reason="activity_not_in_catalog",
                message=message_for("activity_not_in_catalog"),
            )

        if body.activity_code and body.conversation_id:
            await self._record_choice(body.conversation_id, activity.code)

        interpretation = ConsultationInterpretation(
            intent="start_commercial_activity",
            activity=ConsultationActivity(
                normalized_category=activity.code,
                display_name=activity.name,
                confidence=confidence,
                raw_text=activity_raw,
            ),
            location=interpreted.location if interpreted else None,
            activity_candidates=list(interpreted.activity_candidates) if interpreted else [],
            original_query=original_query
            or f"Consulta deterministica: {activity.code} en {address or 'ubicacion confirmada'}",
        )

        # Location resolution
        by_neighborhood = barrio(neighborhood_id) if not address else None
        if body.confirmed_location is not None:
            loc = body.confirmed_location
            location = ConsultationLocation(
                normalized_address=loc.normalized_address,
                commune=normalize_commune(loc.commune),
                neighborhood=loc.neighborhood,
                city=loc.city,
                latitude=loc.latitude,
                longitude=loc.longitude,
                precision=loc.precision,
                status="confirmed",
            )
        elif by_neighborhood is not None:
            location = ConsultationLocation(
                neighborhood=by_neighborhood.nombre,
                neighborhood_id=by_neighborhood.id,
                commune=str(by_neighborhood.comuna),
                city="Ciudad Autonoma de Buenos Aires",
                precision="neighborhood",
                status="neighborhood",
            )
        else:
            if not address:
                return ConsultationResponse(
                    status="needs_clarification",
                    interpretation=interpretation,
                    location=ConsultationLocation(status="pending"),
                    summary=message_for("location_missing"),
                    data_status=DataStatus(overall="blocked", missing=["location"]),
                    reason="location_missing",
                    message=message_for("location_missing"),
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
                    summary=message_for("location_ambiguous", address=address),
                    data_status=DataStatus(
                        overall="blocked",
                        missing=["confirmed_location"],
                        warnings=["ambiguous_address"],
                    ),
                    reason="location_ambiguous",
                    message=message_for("location_ambiguous", address=address),
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
                    summary=message_for("location_outside_caba"),
                    data_status=DataStatus(
                        overall="blocked", missing=["location_in_caba"]
                    ),
                    reason="location_outside_caba",
                    message=message_for("location_outside_caba", address=address),
                )
            if geo.status == "not_found":
                return ConsultationResponse(
                    status="location_not_found",
                    interpretation=interpretation,
                    location=ConsultationLocation(
                        status="not_found",
                        message=geo.message,
                    ),
                    summary=message_for("location_not_found", address=address),
                    data_status=DataStatus(overall="blocked", missing=["location"]),
                    reason="location_not_found",
                    message=message_for("location_not_found", address=address),
                )
            if geo.status == "unavailable":
                # Partial answer: requirements/offices/sources still apply without coordinates.
                location = ConsultationLocation(status="unavailable", message=geo.message)
            else:
                location = ConsultationLocation(
                    normalized_address=geo.normalized_address,
                    commune=geo.commune,
                    neighborhood=geo.neighborhood,
                    neighborhood_id=barrio_por_variante(geo.neighborhood),
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
        reason: str | None = None
        message: str | None = None
        if location.status == "unavailable":
            missing.append("location")
            warnings.append("geocoder_unavailable")
        if approximate and location.status == "confirmed":
            # "A entre B y C": geocoded at the first corner.
            warnings.append("address_approximate")
        if location.status == "neighborhood":
            missing.append("address")
            reason = "location_neighborhood_only"
            message = message_for(reason, neighborhood=location.neighborhood, commune=location.commune)

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
                                published_at=epok_src.published_at.isoformat()
                                if epok_src.published_at
                                else None,
                                license=epok_src.license,
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
            f"{location.normalized_address or (f'el barrio {location.neighborhood}' if location.status == 'neighborhood' else 'la ubicacion consultada')} "
            f"({location.neighborhood or 'barrio N/D'}, "
            f"{f'Comuna {location.commune}' if location.commune else 'comuna N/D'})."
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
            reason=reason,
            message=message,
        )

    async def _record_choice(self, conversation_id: str, code: str) -> None:
        """B16: the rubro the person picked after an unrecognized activity in the same conversation."""
        try:
            row = await self.db.scalar(
                select(UnrecognizedActivity)
                .where(
                    UnrecognizedActivity.conversation_id == conversation_id,
                    UnrecognizedActivity.chosen_code.is_(None),
                )
                .order_by(UnrecognizedActivity.id.desc())
                .limit(1)
            )
            if row is not None:
                row.chosen_code = code
                await self.db.commit()
        except SQLAlchemyError as exc:
            await self.db.rollback()
            logger.warning("Could not record the chosen activity: %r", exc)

    @staticmethod
    def _partial_interpretation(interpreted: InterpretationResponse | None) -> ConsultationInterpretation | None:
        if interpreted is None:
            return None
        return ConsultationInterpretation(
            intent=interpreted.intent,
            activity=ConsultationActivity(
                normalized_category=interpreted.activity.normalized_category,
                display_name=interpreted.activity.display_name,
                confidence=interpreted.activity.confidence,
                raw_text=interpreted.activity.raw_text,
            ),
            location=interpreted.location,
            activity_candidates=list(interpreted.activity_candidates),
            missing_fields=list(interpreted.missing_fields),
            original_query=interpreted.original_query,
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
            req_rows = [r for r in req_rows if r.commune is None or same_commune(r.commune, commune)]

        offices = list(
            await self.db.scalars(
                select(Office)
                .options(selectinload(Office.sources), selectinload(Office.activities))
                .order_by(Office.id)
            )
        )
        offices = [o for o in offices if any(a.id == activity.id for a in o.activities)]
        if commune:
            # Communes come as "Comuna 3" (USIG) or "3" (snapshot): compare the number.
            offices = [o for o in offices if o.commune is None or same_commune(o.commune, commune)]

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
        if commune and latitude is None and neighborhood:
            source_ids.add("source-data-barrios")
            territorial.append(
                TerritorialItem(
                    title="Contexto territorial de la consulta",
                    description=(
                        f"Barrio: {neighborhood}. Comuna: {commune}. "
                        "Ubicacion aproximada por barrio, sin calle ni altura: "
                        "no se puede revisar la zonificacion del lote."
                    ),
                    source_ids=["source-data-barrios"],
                )
            )
        elif commune or latitude is not None:
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
                            published_at=src.published_at.isoformat() if src.published_at else None,
                            license=src.license,
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
