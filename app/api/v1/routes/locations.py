from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.location import GeocodeRequest, GeocodeResponse
from app.schemas.zoning import ZoningOut, ZoningRequest
from app.services.location import LocationService
from app.services.zoning import ZoningService

router = APIRouter(prefix="/locations", tags=["locations"])


def get_location_service(
    settings: Settings = Depends(get_settings),
) -> LocationService:
    return LocationService(settings=settings)


@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_address(
    body: GeocodeRequest,
    service: LocationService = Depends(get_location_service),
) -> GeocodeResponse:
    address = body.address.strip()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="address is required",
        )
    return await service.geocode(address)


@router.post("/zoning", response_model=ZoningOut)
async def lookup_zoning(
    body: ZoningRequest,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> ZoningOut:
    """Parcela (smp) + mixtura + check de rubro via Ciudad 3D / epok."""
    return await ZoningService(settings=settings, db=db).lookup(body)
