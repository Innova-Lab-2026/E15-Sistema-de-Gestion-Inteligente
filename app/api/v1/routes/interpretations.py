from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import AppError, ErrorCode
from app.db.session import get_db
from app.schemas.interpretation import InterpretationRequest, InterpretationResponse
from app.services.interpretation import InterpretationService

router = APIRouter(prefix="/interpretations", tags=["interpretations"])


@router.post("", response_model=InterpretationResponse)
async def interpret_query(
    body: InterpretationRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> InterpretationResponse:
    query = body.query.strip()
    if not query:
        raise AppError(
            ErrorCode.INVALID_REQUEST,
            [{"field": "query", "message": "Campo obligatorio."}],
        )

    # LLM failures never surface here: the service falls back to local rules and reports it in
    # `fallback_reason`.
    service = InterpretationService(settings=settings, db=db)
    return await service.interpret(query)
