from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    example: Optional[str] = None
    enabled: bool
    epok_category_id: Optional[int] = None
    epok_category_name: Optional[str] = None
    epok_rubro_id: Optional[int] = None


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    organization: str
    url: Optional[str] = None
    source_type: str
    jurisdiction: str
    published_at: Optional[datetime] = None
    ingested_at: datetime
    validity_status: str
    transform_rule: Optional[str] = None
    backup_url: Optional[str] = None
    related_activities: Optional[list[str]] = None


class OfficeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    organization: str
    type: str
    address: str
    opening_hours: Optional[str] = None
    url: Optional[str] = None
    latitude: float
    longitude: float
    commune: Optional[str] = None
    neighborhood: Optional[str] = None
    status: str
    source_ids: list[str] = Field(default_factory=list)
    activity_codes: list[str] = Field(default_factory=list)


class RequirementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    status: str
    documents: Optional[list[dict[str, Any]]] = None
    steps: Optional[list[dict[str, Any]]] = None
    activity_code: Optional[str] = None
    commune: Optional[str] = None
    source_ids: list[str] = Field(default_factory=list)
