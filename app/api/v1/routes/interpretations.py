from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.providers.llm import LLMUnavailableError
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="query is required",
        )

    service = InterpretationService(settings=settings, db=db)
    try:
        return await service.interpret(query)
    except LLMUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "llm_unavailable",
                "message": "El proveedor de IA no esta disponible.",
                "detail": str(exc),
            },
        ) from exc
