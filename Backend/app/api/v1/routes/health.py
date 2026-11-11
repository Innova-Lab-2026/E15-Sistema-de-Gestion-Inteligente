import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import AppError, ErrorCode
from app.db import data_files
from app.providers.geocoder import usig_state
from app.providers.llm import LLMClient
from app.db.session import get_db
from app.schemas.error import ErrorResponse
from app.schemas.health import (
    DataFilesStatus,
    EpokStatus,
    GeocoderStatus,
    HealthResponse,
    LLMBackupStatus,
    LLMStatus,
    ProvidersStatus,
    StatusResponse,
)

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


@router.get("/status", response_model=StatusResponse)
async def status(settings: Settings = Depends(get_settings)) -> StatusResponse:
    """Which providers are active (B19): real or simulated geocoder, LLM or local rules, epok.

    Never shows keys or URLs with credentials. Does not call any provider.
    """
    llm = LLMClient(settings)
    primary = next((e for e in llm.endpoints if e.name == "primary"), None)
    backup = next((e for e in llm.endpoints if e.name == "fallback"), None)
    geocoder = (settings.geocoder_provider or "mock").lower()
    epok = (settings.epok_provider or "epok").strip().lower()
    return StatusResponse(
        status="ok",
        app_env=settings.app_env,
        providers=ProvidersStatus(
            llm=LLMStatus(
                active="llm" if llm.is_configured else "rules",
                model=(primary or backup).model if llm.is_configured else None,
                fallback=LLMBackupStatus(configured=backup is not None, model=backup.model if backup else None),
                rules_header=settings.debug,
            ),
            geocoder=GeocoderStatus(
                provider=geocoder,
                simulated=geocoder != "usig",
                breaker_open=geocoder == "usig" and usig_state.is_open,
                cached_addresses=len(usig_state.cache) if geocoder == "usig" else 0,
            ),
            epok=EpokStatus(provider=epok, simulated=epok == "mock"),
        ),
        data=DataFilesStatus(
            barrios=len(data_files.barrios()),
            sinonimos=len(data_files.sinonimos()),
            consultas_prueba=len(data_files.consultas_prueba()),
        ),
    )
