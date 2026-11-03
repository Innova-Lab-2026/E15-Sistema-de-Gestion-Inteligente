from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import register_error_handling
from app.core.logging import configure_logging
from app.db.seed import seed_if_empty
from app.db.session import AsyncSessionLocal
from app.providers.http import close_http_client, open_http_client

logger = logging.getLogger(__name__)


def _warn_unsafe_settings(settings) -> None:
    if settings.app_env in {"local", "test"}:
        return
    if settings.geocoder_provider.lower() == "mock" or settings.epok_provider.lower() == "mock":
        logger.warning("Mock providers enabled with APP_ENV=%s: responses use local fixtures", settings.app_env)
    if settings.debug:
        logger.warning("DEBUG=true with APP_ENV=%s: SQL statements are logged", settings.app_env)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    configure_logging(debug=settings.debug)
    await open_http_client(settings)
    _warn_unsafe_settings(settings)
    if settings.app_env == "local":
        try:
            async with AsyncSessionLocal() as session:
                await seed_if_empty(session)
        except Exception:
            logger.exception(
                "Could not seed catalog on startup; run migrations and seed manually"
            )
    yield
    await close_http_client()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    # Before CORS: CORS must stay outermost so error responses also carry its headers.
    register_error_handling(application)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    return application


app = create_app()
