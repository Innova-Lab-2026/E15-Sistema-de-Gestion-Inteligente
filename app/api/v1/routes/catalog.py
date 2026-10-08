from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models import ActivityCategory, Office, Source
from app.schemas.catalog import ActivityOut, OfficeOut, SourceOut

router = APIRouter(tags=["catalog"])


@router.get("/activities", response_model=list[ActivityOut])
async def list_activities(
    db: AsyncSession = Depends(get_db),
) -> list[ActivityCategory]:
    result = await db.scalars(
        select(ActivityCategory).where(ActivityCategory.enabled.is_(True)).order_by(ActivityCategory.code)
    )
    return list(result)


@router.get("/sources", response_model=list[SourceOut])
async def list_sources(db: AsyncSession = Depends(get_db)) -> list[Source]:
    result = await db.scalars(select(Source).order_by(Source.id))
    return list(result)


@router.get("/offices", response_model=list[OfficeOut])
async def list_offices(
    category: str | None = Query(default=None, description="Activity code filter"),
    commune: str | None = Query(default=None, description="Commune filter"),
    db: AsyncSession = Depends(get_db),
) -> list[OfficeOut]:
    stmt = (
        select(Office)
        .options(selectinload(Office.sources), selectinload(Office.activities))
        .order_by(Office.id)
    )
    offices = list(await db.scalars(stmt))

    items: list[OfficeOut] = []
    for office in offices:
        activity_codes = [a.code for a in office.activities]
        if category and category not in activity_codes:
            continue
        if commune and (
            office.commune is None or office.commune.lower() != commune.lower()
        ):
            continue
        items.append(
            OfficeOut(
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
                status=office.status,
                source_ids=[s.id for s in office.sources],
                activity_codes=activity_codes,
            )
        )
    return items
