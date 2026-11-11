from typing import Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])


class LLMBackupStatus(BaseModel):
    configured: bool
    model: Optional[str] = None


class LLMStatus(BaseModel):
    active: Literal["llm", "rules"] = Field(description="rules = intérprete local sin IA")
    model: Optional[str] = None
    fallback: LLMBackupStatus
    rules_header: bool = Field(
        default=False,
        description='true = con DEBUG, POST /interpretations acepta "X-Interpreter: rules" para no llamar al LLM',
    )


class GeocoderStatus(BaseModel):
    provider: str = Field(examples=["usig", "mock"])
    simulated: bool = Field(description="true = direcciones de prueba, no USIG")
    breaker_open: bool = Field(description="true = USIG falló seguido y por unos minutos no se lo llama")
    cached_addresses: int


class EpokStatus(BaseModel):
    provider: str = Field(examples=["epok", "mock"])
    simulated: bool


class ProvidersStatus(BaseModel):
    llm: LLMStatus
    geocoder: GeocoderStatus
    epok: EpokStatus


class DataFilesStatus(BaseModel):
    barrios: int
    sinonimos: int
    consultas_prueba: int


class StatusResponse(BaseModel):
    status: str = Field(examples=["ok"])
    app_env: str
    providers: ProvidersStatus
    data: DataFilesStatus
