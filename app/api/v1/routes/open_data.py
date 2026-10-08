from typing import Any, Optional

from fastapi import APIRouter, Query

from app.db.ba_data_context import gastronomy_context, load_ba_data_snapshot
from app.schemas.open_data import (
    GastronomyContextOut,
    OpenDataPackageOut,
    OpenDataSnapshotOut,
)

router = APIRouter(prefix="/open-data", tags=["open-data"])


@router.get("/packages", response_model=OpenDataSnapshotOut)
async def list_ba_data_packages() -> OpenDataSnapshotOut:
    """Metadatos BA Data del snapshot ETL local (CKAN package_show)."""
    snap = load_ba_data_snapshot()
    packages = [
        OpenDataPackageOut(
            id=str(p.get("id")),
            title=p.get("title"),
            organization=p.get("organization"),
            license_id=p.get("license_id"),
            url=p.get("url"),
            metadata_modified=p.get("metadata_modified"),
            resources=list(p.get("resources") or []),
        )
        for p in snap.get("packages") or []
        if p.get("id")
    ]
    return OpenDataSnapshotOut(
        source=str(snap.get("source") or "https://data.buenosaires.gob.ar"),
        fetched_at=snap.get("fetched_at"),
        packages=packages,
        gastronomia=snap.get("gastronomia"),
    )


@router.get("/gastronomy-context", response_model=Optional[GastronomyContextOut])
async def get_gastronomy_context(
    commune: Optional[str] = Query(default=None, examples=["Comuna 3", "3"]),
    neighborhood: Optional[str] = Query(default=None, examples=["Balvanera"]),
) -> Optional[GastronomyContextOut]:
    """Conteo de oferta gastronomica BA Data por comuna/barrio (ETL snapshot)."""
    ctx = gastronomy_context(commune=commune, neighborhood=neighborhood)
    if ctx is None:
        return None
    return GastronomyContextOut(**ctx)
