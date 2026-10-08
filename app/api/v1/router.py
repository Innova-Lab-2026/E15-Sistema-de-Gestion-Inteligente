from fastapi import APIRouter

from app.api.v1.routes import catalog, consultations, health, interpretations, locations, open_data

api_router = APIRouter()
api_router.include_router(health.router)

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(catalog.router)
v1_router.include_router(locations.router)
v1_router.include_router(interpretations.router)
v1_router.include_router(consultations.router)
v1_router.include_router(open_data.router)
api_router.include_router(v1_router)
