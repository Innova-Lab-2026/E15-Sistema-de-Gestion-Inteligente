from fastapi import APIRouter, Depends

from app.api.v1.routes import catalog, consultations, health, interpretations, locations, open_data
from app.core.errors import ERROR_RESPONSES, RATE_LIMITED_RESPONSES
from app.core.rate_limit import enforce_rate_limit

# Routes that call external services (LLM, USIG, epok) are rate limited per client.
_rate_limited = {"dependencies": [Depends(enforce_rate_limit)], "responses": RATE_LIMITED_RESPONSES}

api_router = APIRouter()
api_router.include_router(health.router)

v1_router = APIRouter(prefix="/api/v1", responses=ERROR_RESPONSES)
v1_router.include_router(catalog.router)
v1_router.include_router(locations.router, **_rate_limited)
v1_router.include_router(interpretations.router, **_rate_limited)
v1_router.include_router(consultations.router, **_rate_limited)
v1_router.include_router(open_data.router)
api_router.include_router(v1_router)
