from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.consultation import ConsultationRequest, ConsultationResponse
from app.services.consultation import ConsultationService

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("", response_model=ConsultationResponse)
async def create_consultation(
    body: ConsultationRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ConsultationResponse:
    service = ConsultationService(settings=settings, db=db)
    return await service.create(body)
