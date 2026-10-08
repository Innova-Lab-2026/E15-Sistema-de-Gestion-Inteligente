from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from app.schemas.location import LocationCandidate
from app.schemas.zoning import ZoningOut


class ConfirmedLocation(BaseModel):
    normalized_address: str
    latitude: float
    longitude: float
    commune: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = "Ciudad Autonoma de Buenos Aires"
    precision: Optional[str] = "rooftop"


class ConsultationRequest(BaseModel):
    """Deterministic body and/or natural-language query."""

    activity_code: Optional[str] = Field(
        default=None, examples=["rubro_102", "rubro_309"]
    )
    address: Optional[str] = Field(default=None, examples=["Av. Corrientes 2500"])
    query: Optional[str] = Field(
        default=None,
        examples=["Quiero abrir una cafeteria en Av. Corrientes 2500"],
    )
    conversation_id: Optional[str] = None
    confirmed_location: Optional[ConfirmedLocation] = None

    @model_validator(mode="after")
    def require_inputs(self) -> "ConsultationRequest":
        has_deterministic = bool(self.activity_code and self.address)
        has_query = bool(self.query and self.query.strip())
        has_confirmed = self.confirmed_location is not None and bool(self.activity_code)
        if not (has_deterministic or has_query or has_confirmed):
            raise ValueError(
                "Provide activity_code+address, or query, "
                "or activity_code+confirmed_location"
            )
        return self


class ConsultationActivity(BaseModel):
    normalized_category: str
    display_name: str
    confidence: float = 1.0
    raw_text: Optional[str] = None


class ConsultationInterpretation(BaseModel):
    intent: Optional[str] = "start_commercial_activity"
    activity: ConsultationActivity
    original_query: Optional[str] = None


class ConsultationLocation(BaseModel):
    normalized_address: Optional[str] = None
    commune: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    precision: Optional[str] = None
    status: Literal[
        "confirmed", "ambiguous", "out_of_scope", "not_found", "pending"
    ] = "pending"
    candidates: list[LocationCandidate] = Field(default_factory=list)
    message: Optional[str] = None


class DocumentItem(BaseModel):
    name: str
    details: Optional[str] = None
    url_fuente: Optional[str] = None
    source_ids: list[str] = Field(default_factory=list)


class StepItem(BaseModel):
    order: int
    title: str
    description: Optional[str] = None
    url_fuente: Optional[str] = None
    source_ids: list[str] = Field(default_factory=list)


class RequirementItem(BaseModel):
    id: str
    title: str
    description: str
    status: str
    documents: list[DocumentItem] = Field(default_factory=list)
    steps: list[StepItem] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)


class OfficeItem(BaseModel):
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
    distance_meters: Optional[float] = None
    status: str
    source_ids: list[str] = Field(default_factory=list)


class SourceItem(BaseModel):
    id: str
    name: str
    organization: str
    url: Optional[str] = None
    source_type: str
    validity_status: str
    ingested_at: Optional[str] = None


class MapLayerItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    layer_type: str
    url: Optional[str] = None
    status: str
    source_ids: list[str] = Field(default_factory=list)


class TerritorialItem(BaseModel):
    title: str
    description: str
    source_ids: list[str] = Field(default_factory=list)


class DataStatus(BaseModel):
    overall: Literal["complete", "partial", "blocked"] = "complete"
    missing: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


ConsultationStatus = Literal[
    "complete",
    "partial",
    "needs_location_confirmation",
    "needs_clarification",
    "out_of_scope",
    "location_not_found",
    "activity_unknown",
]


class ConsultationResponse(BaseModel):
    consultation_id: str = Field(default_factory=lambda: f"consultation-{uuid4().hex[:12]}")
    status: ConsultationStatus
    interpretation: Optional[ConsultationInterpretation] = None
    location: ConsultationLocation
    summary: str
    requirements: list[RequirementItem] = Field(default_factory=list)
    documents: list[DocumentItem] = Field(default_factory=list)
    steps: list[StepItem] = Field(default_factory=list)
    territorial_information: list[TerritorialItem] = Field(default_factory=list)
    online_procedures: list[OfficeItem] = Field(default_factory=list)
    physical_offices: list[OfficeItem] = Field(default_factory=list)
    map_layers: list[MapLayerItem] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)
    zoning: Optional[ZoningOut] = None
    data_status: DataStatus = Field(default_factory=DataStatus)
    message: Optional[str] = None
