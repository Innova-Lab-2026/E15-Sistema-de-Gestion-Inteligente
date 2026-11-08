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


class ActivityCandidate(BaseModel):
    code: str = Field(examples=["rubro_16"])
    name: str
    score: float = Field(ge=0.0, le=1.0)
    match: Literal["synonym", "llm", "name"] = Field(
        description="synonym: sinónimo exacto · llm: lo propuso el modelo · name: parecido de texto"
    )


class LocationInterpretation(BaseModel):
    raw_text: Optional[str] = None
    address: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    neighborhood_id: Optional[str] = Field(
        default=None, description="barrio_id de data/barrios.csv si la consulta nombra un barrio", examples=["belgrano"]
    )
    neighborhood: Optional[str] = Field(default=None, description="Nombre oficial del barrio", examples=["Belgrano"])
    commune: Optional[str] = Field(default=None, description='Comuna del barrio, "1" a "15"', examples=["13"])
    approximate: bool = Field(
        default=False, description='"Corrientes entre Callao y Riobamba": se usa la primera esquina'
    )


# Why a consultation cannot go on (fixed values: the Frontend picks its text or options from it).
Reason = Literal[
    "activity_missing",
    "activity_not_in_catalog",
    "location_missing",
    "location_neighborhood_only",
    "location_not_found",
    "location_ambiguous",
    "location_outside_caba",
    "topic_out_of_scope",
]
# activity: no rubro · location: neither address nor barrio · address: barrio without street and number
MissingField = Literal["activity", "location", "address"]
MISSING_FIELDS: frozenset[str] = frozenset(MissingField.__args__)

InterpretationStatus = Literal[
    "ready_for_geocoding",
    "needs_clarification",
    "out_of_scope",
    "activity_unknown",
]


INTERPRETATION_STATUSES: frozenset[str] = frozenset(InterpretationStatus.__args__)


class InterpretationResponse(BaseModel):
    intent: Optional[str] = None
    activity: ActivityInterpretation
    location: LocationInterpretation
    jurisdiction: str = "CABA"
    missing_fields: list[MissingField] = Field(default_factory=list)
    activity_candidates: list[ActivityCandidate] = Field(
        default_factory=list,
        description="Hasta 3 rubros habilitados, el mejor primero. Si no hay rubro elegido, para mostrar opciones",
    )
    status: InterpretationStatus
    reason: Optional[Reason] = Field(default=None, description="Por qué falta algo; null si está lista")
    message: Optional[str] = Field(
        default=None, description="Texto para la persona según reason (plantilla del backend, nunca del LLM)"
    )
    provider: str = Field(description="mock | llm")
    fallback_reason: Optional[Literal["llm_unavailable", "llm_rate_limited", "llm_invalid_output"]] = Field(
        default=None,
        description="Set when the LLM is configured but failed and the local rules were used instead",
    )
    original_query: str
