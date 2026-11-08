from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.catalog_data import activity_synonyms
from app.db.data_files import barrio, barrio_por_variante, fold
from app.models import ActivityCategory, UnrecognizedActivity
from app.providers.llm import LLMClient, LLMUnavailableError
from app.providers.address_parser import extract_address, normalize_address
from app.providers.mock_interpreter import mock_interpret
from app.providers.neighborhood_parser import NeighborhoodMatch, find_neighborhood
from app.services.messages import message_for
from app.services.activity_candidates import (
    activity_phrase,
    llm_candidates,
    merge,
    pick,
    rule_candidates,
    similar_candidates,
)
from app.schemas.interpretation import (
    INTERPRETATION_STATUSES,
    MISSING_FIELDS,
    ActivityCandidate,
    ActivityInterpretation,
    InterpretationResponse,
    LocationInterpretation,
)

logger = logging.getLogger(__name__)

INTERPRETATION_PROMPT_VERSION = "interpret-v2"

# Palabras que muestran que la consulta es sobre abrir o habilitar una actividad. Sin ninguna
# de ellas, sin rubro y sin dirección, la consulta queda fuera de tema (topic_out_of_scope).
COMMERCIAL_INTENT_WORDS = {
    "abrir", "abro", "poner", "pongo", "montar", "monto", "habilitar", "habilito", "habilitacion",
    "instalar", "emprender", "emprendimiento", "negocio", "local", "comercio", "comercial",
    "vender", "vendo", "venta", "tienda", "rubro", "actividad", "empresa", "fabrica",
    "taller", "oficina", "inaugurar", "alquilar", "arrancar",
}


def literal_in_query(text: str | None, query: str) -> str | None:
    """`text` if it appears in the query (ignoring case and accents); None if it was paraphrased."""
    if not text or not text.strip():
        return None
    return text.strip() if fold(text) and fold(text) in fold(query) else None

SYSTEM_PROMPT = """Sos un extractor de consultas ciudadanas para CABA (Buenos Aires).
Debes devolver SOLO un JSON valido (sin markdown) con este esquema exacto:
{
  "intent": "start_commercial_activity" o null,
  "activity": {
    "raw_text": string|null,
    "normalized_category": string|null,
    "confidence": number
  },
  "activity_candidates": string[],
  "location": {
    "raw_text": string|null,
    "address": string|null,
    "confidence": number
  },
  "jurisdiction": "CABA",
  "missing_fields": string[],
  "status": "ready_for_geocoding" | "needs_clarification" | "out_of_scope" | "activity_unknown"
}

Reglas:
- El catalogo usa codes `rubro_{id}` con el `epok_rubro_id` y el nombre oficial de Ciudad 3D.
- normalized_category SOLO puede ser uno de esos codes, o null. No inventes rubros.
- activity_candidates: hasta 3 codes del catalogo, del mas al menos parecido a la actividad pedida.
  Completalo siempre que haya una actividad, aunque normalized_category sea null.
- activity.raw_text: las palabras exactas de la consulta que nombran la actividad, sin reescribirlas.
- confidence: de 0 a 1, cuan seguro estas de normalized_category.
- Si la actividad no esta en el catalogo → normalized_category null y status activity_unknown.
- location.address debe ser la mejor direccion extraida (calle y altura si hay).
- missing_fields solo puede tener "activity", "location" o "address".
- Si falta actividad o direccion → needs_clarification. No escribas preguntas ni explicaciones.
- No inventes tramites, coordenadas ni requisitos.
- Intent es start_commercial_activity solo si la persona quiere iniciar una actividad comercial.
"""


class InterpretationService:
    def __init__(self, settings: Settings, db: AsyncSession) -> None:
        self.settings = settings
        self.db = db
        self.llm = LLMClient(settings)
        self.used_model: str | None = None

    async def interpret(self, query: str, conversation_id: str | None = None) -> InterpretationResponse:
        response = await self._interpret(query)
        # Model that answered (main or backup), for the consultation record (B20).
        self.used_model = self.llm.last_model if response.provider == "llm" else None
        if response.reason == "activity_not_in_catalog" and response.activity.raw_text:
            await self._record_unrecognized(response, conversation_id)
        return response

    async def _record_unrecognized(self, response: InterpretationResponse, conversation_id: str | None) -> None:
        """B16: keep what was not recognized for Data. Never breaks the response."""
        try:
            self.db.add(
                UnrecognizedActivity(
                    raw_text=(response.activity.raw_text or "")[:255],
                    candidates=[c.model_dump() for c in response.activity_candidates],
                    conversation_id=conversation_id,
                    provider=response.provider,
                )
            )
            await self.db.commit()
        except SQLAlchemyError as exc:
            await self.db.rollback()
            logger.warning("Could not record unrecognized activity: %r", exc)

    async def _interpret(self, query: str) -> InterpretationResponse:
        catalog = await self._load_catalog()
        fallback_reason: str | None = None

        if self._choose_provider() == "llm":
            try:
                raw = await self._interpret_with_llm(query, catalog)
                return self._validate_and_build(query=query, raw=raw, catalog=catalog, provider="llm")
            except LLMUnavailableError as exc:
                fallback_reason = exc.reason
                logger.warning("LLM unavailable (%s), falling back to mock: %s", exc.reason, exc)
            except (ValueError, TypeError, AttributeError) as exc:
                # JSON object with unexpected types/values (pydantic ValidationError is a ValueError).
                fallback_reason = "llm_invalid_output"
                logger.warning("LLM output failed validation, falling back to mock: %r", exc)

        raw = mock_interpret(query, catalog)
        response = self._validate_and_build(query=query, raw=raw, catalog=catalog, provider="mock")
        response.fallback_reason = fallback_reason
        return response

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
        enabled = {row["code"] for row in json.loads(catalog_json)}
        synonyms_json = json.dumps(
            {term: code for term, code in activity_synonyms().items() if code in enabled},
            ensure_ascii=False,
        )
        user_prompt = (
            f"Catalogo permitido (codes):\n{catalog_json}\n\n"
            f"Sinonimos ciudadanos (termino -> code), usalos para elegir el code:\n{synonyms_json}\n\n"
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
        """Validate a raw interpretation (LLM or rules) into the fixed contract.

        Nothing the LLM writes reaches the response: codes outside the catalog are dropped,
        `raw_text` must appear in the query and `clarification_question` only goes to the logs.
        """
        activity_raw = (raw.get("activity") or {}) if isinstance(raw.get("activity"), dict) else {}
        location_raw = (raw.get("location") or {}) if isinstance(raw.get("location"), dict) else {}

        code = activity_raw.get("normalized_category")
        raw_text = literal_in_query(activity_raw.get("raw_text"), query)
        conf_act = float(activity_raw.get("confidence") or 0.0)
        loc_text = location_raw.get("raw_text") or location_raw.get("address")
        # El LLM puede devolver la altura en palabras ("Monroe dos mil quinientos"): USIG necesita cifras.
        address = normalize_address(location_raw.get("address") or location_raw.get("raw_text"))
        conf_loc = float(location_raw.get("confidence") or 0.0)

        missing = [m for m in (raw.get("missing_fields") or []) if m in MISSING_FIELDS]
        status = raw.get("status") or "needs_clarification"
        if status not in INTERPRETATION_STATUSES:
            raise ValueError(f"invalid interpretation status: {status!r}")
        intent = raw.get("intent")
        display_name = None
        reason: str | None = None
        if provider == "llm" and raw.get("clarification_question"):
            logger.info("LLM clarification_question (not exposed): %r", raw.get("clarification_question"))
        if activity_raw.get("raw_text") and raw_text is None:
            logger.info("Dropped activity.raw_text not present in the query: %r", activity_raw.get("raw_text"))

        invented = isinstance(code, str) and code not in catalog
        if invented:
            logger.info("Dropped activity code outside the catalog: %r", code)

        # B10: synonyms / distinctive official words, the LLM, and text similarity.
        in_scope = self._in_scope(query, intent)
        candidates = merge(
            rule_candidates(query, catalog)
            + (llm_candidates(activity_raw, raw.get("activity_candidates"), catalog) if provider == "llm" else [])
        )
        phrase = raw_text or activity_phrase(query)
        if pick(candidates) is None and in_scope:
            candidates = merge(candidates + similar_candidates(phrase, catalog))
        best = pick(candidates)
        code = best.code if best else None

        if code:
            display_name = catalog[code]
            conf_act = best.score
            if status == "activity_unknown":
                # The rubro came from a synonym or similarity, not from the raw interpretation.
                status = "needs_clarification"
            raw_text = raw_text or (literal_in_query(phrase, query) if best.match == "name" else None)
        else:
            if "activity" not in missing:
                missing.append("activity")
            if status == "ready_for_geocoding":
                status = "activity_unknown"
            if candidates and not raw_text:
                raw_text = literal_in_query(phrase, query)
            if raw_text or candidates or invented:
                status = "activity_unknown"
                reason = "activity_not_in_catalog"
            else:
                reason = "activity_missing"

        parsed_query = extract_address(query)
        neighborhood = find_neighborhood(
            query, skip=[(parsed_query.start, parsed_query.end)] if parsed_query else None
        )
        if address and barrio_por_variante(address):
            # The "address" is only a barrio name ("Palermo"): keep it as the neighborhood.
            neighborhood = neighborhood or self._neighborhood_from_id(barrio_por_variante(address))
            address = loc_text = None

        if not address and not loc_text:
            if neighborhood:
                # Barrio without street and number: enough for procedures and the communal
                # office; the address is still needed for zoning.
                missing = [m for m in missing if m != "location"]
                if "address" not in missing:
                    missing.append("address")
            elif "location" not in missing:
                missing.append("location")
            if status == "ready_for_geocoding":
                status = "needs_clarification"
        else:
            address = address or loc_text
            loc_text = loc_text or address
            conf_loc = max(conf_loc, 0.5)

        if code and address and status not in {"out_of_scope", "activity_unknown"}:
            status = "ready_for_geocoding"
            missing = [m for m in missing if m not in {"activity", "location", "address"}]
            intent = intent or "start_commercial_activity"

        if not code and not address and not self._in_scope(query, intent):
            # Not about opening an activity ("cómo saco el DNI", "qué clima hace").
            status = "out_of_scope"
            reason = "topic_out_of_scope"
        elif code and status != "ready_for_geocoding":
            if not address and not loc_text:
                reason = "location_neighborhood_only" if neighborhood else "location_missing"
            elif status == "out_of_scope":
                reason = "topic_out_of_scope"
            else:
                reason = "activity_not_in_catalog"

        return InterpretationResponse(
            intent=intent,
            activity=ActivityInterpretation(
                raw_text=raw_text,
                normalized_category=code,
                display_name=display_name,
                confidence=min(max(conf_act, 0.0), 1.0),
            ),
            activity_candidates=[
                ActivityCandidate(code=c.code, name=c.name, score=c.score, match=c.match) for c in candidates
            ],
            location=LocationInterpretation(
                raw_text=loc_text,
                address=address,
                confidence=min(max(conf_loc, 0.0), 1.0),
                neighborhood_id=neighborhood.barrio_id if neighborhood else None,
                neighborhood=neighborhood.name if neighborhood else None,
                commune=str(neighborhood.commune) if neighborhood else None,
                approximate=bool(
                    address and parsed_query and parsed_query.approximate and parsed_query.address == address
                ),
            ),
            jurisdiction=str(raw.get("jurisdiction") or "CABA"),
            missing_fields=missing,
            status=status,  # type: ignore[arg-type]
            reason=reason,  # type: ignore[arg-type]
            message=message_for(
                reason,  # type: ignore[arg-type]
                activity_text=raw_text,
                has_candidates=bool(candidates),
                address=address,
                neighborhood=neighborhood.name if neighborhood else None,
                commune=str(neighborhood.commune) if neighborhood else None,
            ),
            provider=provider,
            original_query=query,
        )

    @staticmethod
    def _in_scope(query: str, intent: str | None) -> bool:
        if intent == "start_commercial_activity":
            return True
        words = set(fold(query).split())
        return bool(words & COMMERCIAL_INTENT_WORDS)

    @staticmethod
    def _neighborhood_from_id(barrio_id: str | None) -> NeighborhoodMatch | None:
        found = barrio(barrio_id)
        if found is None:
            return None
        return NeighborhoodMatch(
            barrio_id=found.id, name=found.nombre, commune=found.comuna, raw_text=found.nombre, start=0, end=0
        )
