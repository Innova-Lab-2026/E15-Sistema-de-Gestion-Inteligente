from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.limits import MAX_CODE_LENGTH, MAX_QUERY_LENGTH


class InterpretationRequest(BaseModel):
    query: str = Field(min_length=1, max_length=MAX_QUERY_LENGTH, examples=[
        "Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?"
    ])
    conversation_id: Optional[str] = Field(default=None, max_length=MAX_CODE_LENGTH)
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
    fallback_reason: Optional[Literal["llm_unavailable", "llm_rate_limited", "llm_invalid_output"]] = Field(
        default=None,
        description="Set when the LLM is configured but failed and the local rules were used instead",
    )
    original_query: str
