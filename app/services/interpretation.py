from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import ActivityCategory
from app.providers.llm import LLMClient, LLMUnavailableError
from app.providers.mock_interpreter import mock_interpret
from app.schemas.interpretation import (
    ActivityInterpretation,
    InterpretationResponse,
    LocationInterpretation,
)

logger = logging.getLogger(__name__)

INTERPRETATION_PROMPT_VERSION = "interpret-v1"

SYSTEM_PROMPT = """Sos un extractor de consultas ciudadanas para CABA (Buenos Aires).
Debes devolver SOLO un JSON valido (sin markdown) con este esquema exacto:
{
  "intent": "start_commercial_activity" o null,
  "activity": {
    "raw_text": string|null,
    "normalized_category": string|null,
    "confidence": number
  },
  "location": {
    "raw_text": string|null,
    "address": string|null,
    "confidence": number
  },
  "jurisdiction": "CABA",
  "missing_fields": string[],
  "clarification_question": string|null,
  "status": "ready_for_geocoding" | "needs_clarification" | "out_of_scope" | "activity_unknown"
}

Reglas:
- normalized_category SOLO puede ser uno de los codigos del catalogo provisto, o null.
- El catalogo usa codes `rubro_{id}` con el `epok_rubro_id` y el nombre oficial de Ciudad 3D.
- normalized_category SOLO puede ser uno de esos codes, o null. No inventes rubros.
- Si la actividad no esta en el catalogo → status activity_unknown o out_of_scope, no inventes otro codigo.
- location.address debe ser la mejor direccion extraida (calle y altura si hay).
- Si falta actividad o direccion → needs_clarification y pregunta en espanol.
- No inventes tramites, coordenadas ni requisitos.
- Intent es start_commercial_activity solo si la persona quiere iniciar una actividad comercial.
"""


class InterpretationService:
    def __init__(self, settings: Settings, db: AsyncSession) -> None:
        self.settings = settings
        self.db = db
        self.llm = LLMClient(settings)

    async def interpret(self, query: str) -> InterpretationResponse:
        catalog = await self._load_catalog()
        provider = self._choose_provider()

        if provider == "llm":
            try:
                raw = await self._interpret_with_llm(query, catalog)
            except LLMUnavailableError as exc:
                logger.warning("LLM unavailable, falling back to mock: %s", exc)
                raw = mock_interpret(query, catalog)
                provider = "mock"
        else:
            raw = mock_interpret(query, catalog)

        return self._validate_and_build(query=query, raw=raw, catalog=catalog, provider=provider)

    def _choose_provider(self) -> str:
        # Prefer LLM when configured; otherwise mock for local testing.
        if self.llm.is_configured:
            return "llm"
        return "mock"

    async def _load_catalog(self) -> dict[str, str]:
        rows = await self.db.scalars(
            select(ActivityCategory).where(ActivityCategory.enabled.is_(True))
        )
        return {row.code: row.name for row in rows}

    async def _interpret_with_llm(
        self, query: str, catalog: dict[str, str]
    ) -> dict[str, Any]:
        rows = await self.db.scalars(
            select(ActivityCategory).where(ActivityCategory.enabled.is_(True))
        )
        catalog_json = json.dumps(
            [
                {
                    "code": row.code,
                    "name": row.name,
                    "epok_rubro_id": row.epok_rubro_id,
                    "epok_category_id": row.epok_category_id,
                    "epok_category_name": row.epok_category_name,
                }
                for row in rows
            ],
            ensure_ascii=False,
        )
        user_prompt = (
            f"Catalogo permitido (codes):\n{catalog_json}\n\n"
            f"Consulta ciudadana:\n{query}\n"
        )
        return await self.llm.complete_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    def _validate_and_build(
        self,
        *,
        query: str,
        raw: dict[str, Any],
        catalog: dict[str, str],
        provider: str,
    ) -> InterpretationResponse:
        activity_raw = (raw.get("activity") or {}) if isinstance(raw.get("activity"), dict) else {}
        location_raw = (raw.get("location") or {}) if isinstance(raw.get("location"), dict) else {}

        code = activity_raw.get("normalized_category")
        raw_text = activity_raw.get("raw_text")
        conf_act = float(activity_raw.get("confidence") or 0.0)
        loc_text = location_raw.get("raw_text") or location_raw.get("address")
        address = location_raw.get("address") or location_raw.get("raw_text")
        conf_loc = float(location_raw.get("confidence") or 0.0)

        missing = list(raw.get("missing_fields") or [])
        status = raw.get("status") or "needs_clarification"
        question = raw.get("clarification_question")
        intent = raw.get("intent")
        display_name = None

        if code and code not in catalog:
            # Model invented a category — reject
            code = None
            display_name = None
            status = "out_of_scope"
            question = (
                "La actividad detectada no pertenece al catalogo del MVP "
                f"({', '.join(sorted(catalog.keys()))}). "
                "Reformula la consulta con una actividad soportada."
            )
            if "activity" not in missing:
                missing.append("activity")
        elif code:
            display_name = catalog[code]
            conf_act = max(conf_act, 0.5)
        else:
            if "activity" not in missing:
                missing.append("activity")
            if status == "ready_for_geocoding":
                status = "activity_unknown"
            if not question:
                question = (
                    "No pude clasificar la actividad en el catalogo del MVP. "
                    f"Actividades soportadas: {', '.join(sorted(catalog.keys()))}."
                )

        if not address and not loc_text:
            if "location" not in missing:
                missing.append("location")
            if status == "ready_for_geocoding":
                status = "needs_clarification"
            if not question:
                question = (
                    "Falta una direccion con calle y altura en CABA para continuar."
                )
        else:
            address = address or loc_text
            loc_text = loc_text or address
            conf_loc = max(conf_loc, 0.5)

        if code and address and status not in {"out_of_scope", "activity_unknown"}:
            status = "ready_for_geocoding"
            missing = [m for m in missing if m not in {"activity", "location"}]
            question = None
            intent = intent or "start_commercial_activity"

        return InterpretationResponse(
            intent=intent,
            activity=ActivityInterpretation(
                raw_text=raw_text,
                normalized_category=code,
                display_name=display_name,
                confidence=min(max(conf_act, 0.0), 1.0),
            ),
            location=LocationInterpretation(
                raw_text=loc_text,
                address=address,
                confidence=min(max(conf_loc, 0.0), 1.0),
            ),
            jurisdiction=str(raw.get("jurisdiction") or "CABA"),
            missing_fields=missing,
            clarification_question=question,
            status=status,  # type: ignore[arg-type]
            provider=provider,
            original_query=query,
        )
