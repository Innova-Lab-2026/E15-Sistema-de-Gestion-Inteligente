from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class InterpretationRequest(BaseModel):
    query: str = Field(min_length=1, examples=[
        "Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?"
    ])
    conversation_id: Optional[str] = None
    confirmed_location: Optional[dict[str, Any]] = None


class ActivityInterpretation(BaseModel):
    raw_text: Optional[str] = None
    normalized_category: Optional[str] = None
    display_name: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class LocationInterpretation(BaseModel):
    raw_text: Optional[str] = None
    address: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


InterpretationStatus = Literal[
    "ready_for_geocoding",
    "needs_clarification",
    "out_of_scope",
    "activity_unknown",
]


class InterpretationResponse(BaseModel):
    intent: Optional[str] = None
    activity: ActivityInterpretation
    location: LocationInterpretation
    jurisdiction: str = "CABA"
    missing_fields: list[str] = Field(default_factory=list)
    clarification_question: Optional[str] = None
    status: InterpretationStatus
    provider: str = Field(description="mock | llm")
    original_query: str
