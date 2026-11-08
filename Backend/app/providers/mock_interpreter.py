"""Rule-based interpreter for local tests without an LLM key."""

from __future__ import annotations

from typing import Any

from app.db.catalog_data import ACTIVITY_DEFINITIONS, activity_synonyms
from app.db.data_files import fold
from app.providers.address_parser import extract_address

# Palabras de los nombres oficiales: respaldo cuando ningun sinonimo coincide.
# Longer / more specific keywords first
_ACTIVITY_KEYWORDS: list[tuple[str, tuple[str, ...]]] = sorted(
    [(code, keywords) for code, _n, _e, _eid, _rid, keywords in ACTIVITY_DEFINITIONS],
    key=lambda item: -max((len(k) for k in item[1]), default=0),
)


def _synonyms_longest_first() -> list[tuple[str, str]]:
    return sorted(activity_synonyms().items(), key=lambda item: -len(item[0]))


def _find_activity(text: str, catalog: dict[str, str]) -> tuple[str, str] | None:
    """(rubro_code, termino tal cual en la consulta). Sinonimos primero, el mas largo gana."""
    folded = fold(text)
    for term, code in _synonyms_longest_first():
        if code in catalog and term in folded:
            return code, term
    lower = text.lower()
    for code, keywords in _ACTIVITY_KEYWORDS:
        if code not in catalog:
            continue
        for kw in keywords:
            if kw in lower:
                return code, kw
    return None


def mock_interpret(query: str, catalog: dict[str, str]) -> dict[str, Any]:
    """Return a raw interpretation dict (pre-validation). catalog: code -> display_name."""
    text = query.strip()

    found = _find_activity(text, catalog)
    activity_code, activity_raw = found if found else (None, None)

    parsed = extract_address(text)
    address_raw = parsed.raw_text if parsed else None
    address = parsed.address if parsed else None

    intent = "start_commercial_activity" if activity_code else None
    missing: list[str] = []
    if not activity_code:
        missing.append("activity")
    if not address_raw:
        missing.append("location")

    catalog_preview = ", ".join(sorted(catalog.keys())[:8])
    if len(catalog) > 8:
        catalog_preview += ", ..."

    if activity_code and address_raw:
        status = "ready_for_geocoding"
        question = None
    elif activity_code and not address_raw:
        status = "needs_clarification"
        question = (
            f'Detecte la actividad "{catalog.get(activity_code, activity_code)}", '
            "pero falta una direccion con calle y altura en CABA. "
            "Indica la direccion para continuar."
        )
    elif address_raw and not activity_code:
        status = "activity_unknown"
        question = (
            "Detecte una direccion, pero la actividad no esta en el catalogo del MVP "
            f"({catalog_preview}). Reformula la actividad o consulta el listado /activities."
        )
    else:
        status = "needs_clarification"
        question = (
            "No pude detectar actividad ni direccion. "
            'Ejemplo: "Quiero abrir una ferreteria en Santiago del Estero 112".'
        )

    return {
        "intent": intent,
        "activity": {
            "raw_text": activity_raw,
            "normalized_category": activity_code,
            "display_name": catalog.get(activity_code) if activity_code else None,
            "confidence": 0.85 if activity_code else 0.0,
        },
        "location": {
            "raw_text": address_raw,
            "address": address,
            "confidence": 0.85 if address_raw else 0.0,
        },
        "jurisdiction": "CABA",
        "missing_fields": missing,
        "clarification_question": question,
        "status": status,
    }
