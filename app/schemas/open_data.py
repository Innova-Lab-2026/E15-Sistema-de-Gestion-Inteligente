from typing import Any, Optional

from pydantic import BaseModel, Field


class OpenDataPackageOut(BaseModel):
    id: str
    title: Optional[str] = None
    organization: Optional[str] = None
    license_id: Optional[str] = None
    url: Optional[str] = None
    metadata_modified: Optional[str] = None
    resources: list[dict[str, Any]] = Field(default_factory=list)


class GastronomyContextOut(BaseModel):
    dataset: str
    dataset_url: str
    total_caba: Optional[int] = None
    comuna: Optional[str] = None
    count_comuna: Optional[int] = None
    barrio: Optional[str] = None
    count_barrio: Optional[int] = None
    by_categoria: Optional[dict[str, int]] = None
    csv_url: Optional[str] = None
    geojson_url: Optional[str] = None
    fetched_at: Optional[str] = None
    source_ids: list[str] = Field(default_factory=list)


class OpenDataSnapshotOut(BaseModel):
    source: str
    fetched_at: Optional[str] = None
    packages: list[OpenDataPackageOut] = Field(default_factory=list)
    gastronomia: Optional[dict[str, Any]] = None
