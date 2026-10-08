from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
    address: str = Field(min_length=1, examples=["Av. Corrientes 2500"])


class GeocodeSource(BaseModel):
    id: str
    name: str
    retrieved_at: datetime


class LocationCandidate(BaseModel):
    normalized_address: str
    city: str = "Ciudad Autonoma de Buenos Aires"
    commune: Optional[str] = None
    neighborhood: Optional[str] = None
    latitude: float
    longitude: float
    precision: str = "rooftop"


class GeocodeResponse(BaseModel):
    status: Literal["confirmed", "ambiguous", "out_of_scope", "not_found"]
    original_address: str
    normalized_address: Optional[str] = None
    city: Optional[str] = None
    commune: Optional[str] = None
    neighborhood: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    precision: Optional[str] = None
    candidates: list[LocationCandidate] = Field(default_factory=list)
    source: Optional[GeocodeSource] = None
    message: Optional[str] = None
