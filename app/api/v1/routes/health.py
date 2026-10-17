import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, ErrorCode
from app.db.session import get_db
from app.schemas.error import ErrorResponse
from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness: the process answers. Does not touch the database."""
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    response_model=HealthResponse,
    responses={503: {"model": ErrorResponse, "description": "Database unavailable"}},
)
async def ready(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Readiness for the hosting: the database answers and the schema is migrated."""
    try:
        await db.execute(text("SELECT 1 FROM activity_categories LIMIT 1"))
    except (SQLAlchemyError, OSError) as exc:
        logger.warning("Readiness check failed: %r", exc)
        raise AppError(ErrorCode.DATABASE_UNAVAILABLE) from exc
    return HealthResponse(status="ready")
