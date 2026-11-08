from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import AppError, ErrorCode
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


@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(
    consultation_id: str = Path(max_length=64),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ConsultationResponse:
    """The stored answer of a previous consultation (B20)."""
    found = await ConsultationService(settings=settings, db=db).get(consultation_id)
    if found is None:
        raise AppError(ErrorCode.NOT_FOUND, [{"field": "consultation_id", "message": "No existe esa consulta."}])
    return found
