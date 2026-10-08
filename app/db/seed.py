"""Seed / sync catalog MVP alineado a epok."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.ba_data_context import map_layer_defs_from_snapshot
from app.db.catalog_data import ACTIVITY_DEFINITIONS, EPOK_CATEGORIES
from app.db.offices_data import office_defs_from_snapshot
from app.db.tramites_curados import (
    CURATED_AT,
    URL_GUIA_LOCAL,
    URL_HABILITACION,
    URL_HABILITACION_EXPRES,
    commercial_habilitation_guide,
    uses_curated_commercial_guide,
)
from app.db.session import AsyncSessionLocal
from app.models import (
    ActivityCategory,
    MapLayer,
    Office,
    Requirement,
    Source,
)

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _activity_id(code: str) -> str:
    return f"activity-{code}"


def _requirement_id(code: str) -> str:
    return f"requirement-{code}"


async def _ensure_sources(session: AsyncSession) -> dict[str, Source]:
    pilot_codes = sorted(
        c[0]
        for c in ACTIVITY_DEFINITIONS
        if uses_curated_commercial_guide(
            activity_code=c[0], epok_category_id=c[3]
        )
    )
    wanted = {
        "source-001": Source(
            id="source-001",
            name="Guia GCBA: como habilitar tu local comercial",
            organization="GCBA",
            url=URL_GUIA_LOCAL,
            source_type="procedures",
            jurisdiction="CABA",
            published_at=CURATED_AT,
            ingested_at=_utcnow(),
            validity_status="available",
            transform_rule="tramites-curados-v1",
            backup_url="https://www.buenosaires.gob.ar/tramites",
            related_activities=pilot_codes,
        ),
        "source-002": Source(
            id="source-002",
            name="BA Data - oferta gastronomica / comunas / barrios",
            organization="GCBA / BA Data (CKAN)",
            url="https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos",
            source_type="territorial",
            jurisdiction="CABA",
            published_at=_utcnow(),
            ingested_at=_utcnow(),
            validity_status="available",
            transform_rule="ba-data-etl-v1",
            backup_url="https://data.buenosaires.gob.ar",
            related_activities=[
                c[0]
                for c in ACTIVITY_DEFINITIONS
                if c[0]
                in {
                    "rubro_102",
                    "rubro_471",
                    "rubro_16",
                    "rubro_137",
                    "rubro_169",
                    "rubro_245",
                }
            ],
        ),
        "source-003": Source(
            id="source-003",
            name="AGC + Sedes Comunales (BA Data / oficiales)",
            organization="GCBA / BA Data / AGC",
            url="https://data.buenosaires.gob.ar/dataset/sedes-comunales",
            source_type="offices",
            jurisdiction="CABA",
            published_at=_utcnow(),
            ingested_at=_utcnow(),
            validity_status="available",
            transform_rule="offices-snapshot-v1",
            backup_url=URL_HABILITACION,
            related_activities=[c[0] for c in ACTIVITY_DEFINITIONS],
        ),
        "source-004": Source(
            id="source-004",
            name="Ciudad 3D / epok rubros oficiales",
            organization="GCBA / USIG",
            url="https://epok.buenosaires.gob.ar/cur3d/cuadrosdeuso/rubros/",
            source_type="normative",
            jurisdiction="CABA",
            published_at=_utcnow(),
            ingested_at=_utcnow(),
            validity_status="available",
            transform_rule="epok-rubros-snapshot-v1",
            backup_url="https://ciudad3d.buenosaires.gob.ar/",
            related_activities=[c[0] for c in ACTIVITY_DEFINITIONS],
        ),
        "source-005": Source(
            id="source-005",
            name="Habilitacion de actividad economica (GCBA)",
            organization="GCBA / AGC",
            url=URL_HABILITACION,
            source_type="procedures",
            jurisdiction="CABA",
            published_at=CURATED_AT,
            ingested_at=_utcnow(),
            validity_status="available",
            transform_rule="tramites-curados-v1",
            backup_url=URL_GUIA_LOCAL,
            related_activities=pilot_codes,
        ),
        "source-006": Source(
            id="source-006",
            name="Habilitacion de actividad economica expres (GCBA)",
            organization="GCBA / AGC",
            url=URL_HABILITACION_EXPRES,
            source_type="procedures",
            jurisdiction="CABA",
            published_at=CURATED_AT,
            ingested_at=_utcnow(),
            validity_status="available",
            transform_rule="tramites-curados-v1",
            backup_url=URL_GUIA_LOCAL,
            related_activities=pilot_codes,
        ),
        "source-007": Source(
            id="source-007",
            name="Ciudad 3D (visor normativa del lote)",
            organization="GCBA / USIG",
            url="https://ciudad3d.buenosaires.gob.ar/",
            source_type="normative",
            jurisdiction="CABA",
            published_at=CURATED_AT,
            ingested_at=_utcnow(),
            validity_status="available",
            transform_rule="tramites-curados-v1",
            backup_url="https://epok.buenosaires.gob.ar/cur3d/categorias/",
            related_activities=pilot_codes,
        ),
    }

    existing = {
        s.id: s
        for s in (
            await session.scalars(select(Source).where(Source.id.in_(list(wanted))))
        ).all()
    }
    for sid, src in wanted.items():
        if sid in existing:
            row = existing[sid]
            row.name = src.name
            row.organization = src.organization
            row.url = src.url
            row.source_type = src.source_type
            row.transform_rule = src.transform_rule
            row.related_activities = src.related_activities
            row.published_at = src.published_at
            row.ingested_at = _utcnow()
            row.validity_status = src.validity_status
            row.backup_url = src.backup_url
        else:
            session.add(src)
            existing[sid] = src
    await session.flush()
    return existing


async def _sync_activities(session: AsyncSession) -> list[ActivityCategory]:
    existing = {
        a.code: a for a in (await session.scalars(select(ActivityCategory))).all()
    }
    wanted_codes = {c[0] for c in ACTIVITY_DEFINITIONS}
    result: list[ActivityCategory] = []
    for code, name, example, epok_id, rubro_id, _keywords in ACTIVITY_DEFINITIONS:
        epok_name = EPOK_CATEGORIES.get(epok_id) or str(epok_id)
        if code in existing:
            row = existing[code]
            row.name = name
            row.example = example
            row.enabled = True
            row.epok_category_id = epok_id
            row.epok_category_name = epok_name
            row.epok_rubro_id = rubro_id
            result.append(row)
        else:
            row = ActivityCategory(
                id=_activity_id(code),
                code=code,
                name=name,
                example=example,
                enabled=True,
                epok_category_id=epok_id,
                epok_category_name=epok_name,
                epok_rubro_id=rubro_id,
            )
            session.add(row)
            result.append(row)
    # Desactivar codigos legacy (inventados / previos) que ya no estan en epok
    for code, row in existing.items():
        if code not in wanted_codes:
            row.enabled = False
    await session.flush()
    return result


async def _sync_requirements(
    session: AsyncSession,
    activities: list[ActivityCategory],
    sources: dict[str, Source],
) -> None:
    source_tramites = sources["source-001"]
    source_epok = sources["source-004"]
    curated_source_ids = [
        "source-001",
        "source-005",
        "source-006",
        "source-007",
        "source-004",
    ]

    # Remove legacy seed requirement ids from stage 1 (replaced by requirement-{code})
    legacy = await session.scalars(
        select(Requirement).where(
            Requirement.id.in_(
                ["requirement-001", "requirement-002", "requirement-003"]
            )
        )
    )
    for row in legacy:
        await session.delete(row)
    await session.flush()

    existing = {
        r.id: r
        for r in (
            await session.scalars(
                select(Requirement).options(selectinload(Requirement.sources))
            )
        ).all()
    }

    for activity in activities:
        rid = _requirement_id(activity.code)
        curated = uses_curated_commercial_guide(
            activity_code=activity.code,
            epok_category_id=activity.epok_category_id,
        )
        if curated:
            guide = commercial_habilitation_guide(
                activity.name, activity.epok_rubro_id
            )
            title = guide["title"]
            description = guide["description"]
            documents = guide["documents"]
            steps = guide["steps"]
            status = guide["status"]
            linked = [
                sources[sid] for sid in curated_source_ids if sid in sources
            ]
        else:
            title = f"Habilitacion orientativa - {activity.name}"
            description = (
                f"Orientacion seed generica para {activity.name} "
                f"(codigo {activity.code}). "
                f"Categoria Ciudad 3D / epok: {activity.epok_category_id} - "
                f"{activity.epok_category_name}. "
                f"Rubro oficial epok_id={activity.epok_rubro_id}. "
                "Aun no hay guia de tramites curada para este rubro; "
                f"consultar {URL_GUIA_LOCAL} y validar en fuentes oficiales."
            )
            documents = [
                {
                    "name": "Documentacion del titular",
                    "details": "DNI vigente del titular o apoderado",
                    "url_fuente": URL_GUIA_LOCAL,
                },
                {
                    "name": "Documentacion del local",
                    "details": (
                        "Segun rubro y tipo de habilitacion (comun / expres). "
                        f"Ver {URL_HABILITACION}"
                    ),
                    "url_fuente": URL_HABILITACION,
                },
            ]
            steps = [
                {
                    "order": 1,
                    "title": "Verificar uso permitido del lote",
                    "description": (
                        "Consultar Ciudad 3D / normativa urbanistica para el punto "
                        f"(categoria epok {activity.epok_category_id})."
                    ),
                    "url_fuente": "https://ciudad3d.buenosaires.gob.ar/",
                },
                {
                    "order": 2,
                    "title": "Iniciar habilitacion de actividad economica",
                    "description": (
                        "Seguir la guia oficial de tramites GCBA (miBA / AGC)."
                    ),
                    "url_fuente": URL_HABILITACION,
                },
                {
                    "order": 3,
                    "title": "Completar documentacion y autoproteccion",
                    "description": (
                        "Segun tipo de local y superficie publicada oficialmente."
                    ),
                    "url_fuente": URL_GUIA_LOCAL,
                },
            ]
            status = "available"
            linked = [source_tramites, source_epok]

        if rid in existing:
            row = existing[rid]
            row.title = title
            row.description = description
            row.documents = documents
            row.steps = steps
            row.activity_id = activity.id
            row.status = status
            for src in linked:
                if src not in row.sources:
                    row.sources.append(src)
        else:
            session.add(
                Requirement(
                    id=rid,
                    title=title,
                    description=description,
                    status=status,
                    documents=documents,
                    steps=steps,
                    activity_id=activity.id,
                    commune=None,
                    sources=list(linked),
                )
            )
    await session.flush()


async def _upsert_office(
    session: AsyncSession,
    *,
    spec: dict,
    activities: list[ActivityCategory],
    source_offices: Source,
) -> None:
    office = await session.scalar(
        select(Office)
        .where(Office.id == spec["id"])
        .options(selectinload(Office.activities), selectinload(Office.sources))
    )
    if office is None:
        session.add(
            Office(
                id=spec["id"],
                name=spec["name"],
                organization=spec["organization"],
                type=spec["type"],
                address=spec["address"],
                opening_hours=spec.get("opening_hours"),
                url=spec.get("url"),
                latitude=spec["latitude"],
                longitude=spec["longitude"],
                commune=spec.get("commune"),
                neighborhood=spec.get("neighborhood"),
                status=spec.get("status", "available"),
                activities=list(activities),
                sources=[source_offices],
            )
        )
        return

    office.name = spec["name"]
    office.organization = spec["organization"]
    office.type = spec["type"]
    office.address = spec["address"]
    office.opening_hours = spec.get("opening_hours")
    office.url = spec.get("url")
    office.latitude = spec["latitude"]
    office.longitude = spec["longitude"]
    office.commune = spec.get("commune")
    office.neighborhood = spec.get("neighborhood")
    office.status = spec.get("status", "available")
    office.activities = list(activities)
    if source_offices not in office.sources:
        office.sources.append(source_offices)


async def _sync_offices_and_layers(
    session: AsyncSession,
    activities: list[ActivityCategory],
    sources: dict[str, Source],
) -> None:
    source_offices = sources["source-003"]
    source_territorial = sources["source-002"]

    office_defs = office_defs_from_snapshot()
    if not office_defs:
        logger.warning(
            "offices_snapshot.json vacio o ausente; correr scripts/fetch_offices.py"
        )
    wanted_ids = {spec["id"] for spec in office_defs}
    for spec in office_defs:
        await _upsert_office(
            session,
            spec=spec,
            activities=activities,
            source_offices=source_offices,
        )

    # Retirar oficinas inventadas / fuera del snapshot oficial
    existing = (
        await session.scalars(select(Office).options(selectinload(Office.activities)))
    ).all()
    for office in existing:
        if office.id not in wanted_ids:
            await session.delete(office)

    layer = await session.get(MapLayer, "layer-001")
    if layer is None:
        session.add(
            MapLayer(
                id="layer-001",
                name="Uso del suelo (referencia Ciudad 3D)",
                description="Capa territorial de referencia (epok / Codigo Urbanistico)",
                layer_type="geojson",
                url="https://ciudad3d.buenosaires.gob.ar/",
                status="available",
                sources=[source_territorial],
            )
        )
    else:
        layer.name = "Uso del suelo (referencia Ciudad 3D)"
        layer.description = "Capa territorial de referencia (epok / Codigo Urbanistico)"
        layer.url = "https://ciudad3d.buenosaires.gob.ar/"

    for spec in map_layer_defs_from_snapshot():
        existing_layer = await session.get(MapLayer, spec["id"])
        if existing_layer is None:
            session.add(
                MapLayer(
                    id=spec["id"],
                    name=spec["name"],
                    description=spec.get("description"),
                    layer_type=spec.get("layer_type", "geojson"),
                    url=spec.get("url"),
                    status=spec.get("status", "available"),
                    sources=[source_territorial],
                )
            )
        else:
            existing_layer.name = spec["name"]
            existing_layer.description = spec.get("description")
            existing_layer.layer_type = spec.get("layer_type", "geojson")
            existing_layer.url = spec.get("url")
            existing_layer.status = spec.get("status", "available")
    await session.flush()


async def sync_catalog(session: AsyncSession) -> int:
    """Upsert full medium catalog. Returns number of activities."""
    sources = await _ensure_sources(session)
    activities = await _sync_activities(session)
    await _sync_requirements(session, activities, sources)
    await _sync_offices_and_layers(session, activities, sources)
    await session.commit()
    logger.info("Catalog synced: %s activities (epok-aligned)", len(activities))
    return len(activities)


async def seed_if_empty(session: AsyncSession) -> bool:
    """Compatibility: always sync catalog (safe upsert)."""
    count = await sync_catalog(session)
    return count > 0


async def run_seed() -> None:
    async with AsyncSessionLocal() as session:
        await sync_catalog(session)


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
