"""Rule-based interpreter for local tests without an LLM key."""

from __future__ import annotations

import re
from typing import Any

from app.db.catalog_data import ACTIVITY_DEFINITIONS

_ADDRESS_PATTERNS = [
    re.compile(
        r"(?:en|sobre)\s+(?P<addr>(?:av(?:\.|enida)?|calle|diag(?:\.|onal)?)\s+[^,?\.]+?\s+\d{1,5})",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<addr>(?:av(?:\.|enida)?\.?\s+)?(?:corrientes|santa\s+fe|rivadavia|del\s+libertador|cabildo|cordoba|callao|9\s+de\s+julio|santiago\s+del\s+estero)[^,?\.]*?\s+\d{1,5})",
        re.IGNORECASE,
    ),
]

# Longer / more specific keywords first
_ACTIVITY_KEYWORDS: list[tuple[str, tuple[str, ...]]] = sorted(
    [(code, keywords) for code, _n, _e, _eid, _rid, keywords in ACTIVITY_DEFINITIONS],
    key=lambda item: -max((len(k) for k in item[1]), default=0),
)


def mock_interpret(query: str, catalog: dict[str, str]) -> dict[str, Any]:
    """Return a raw interpretation dict (pre-validation). catalog: code -> display_name."""
    text = query.strip()
    lower = text.lower()

    activity_code: str | None = None
    activity_raw: str | None = None
    for code, keywords in _ACTIVITY_KEYWORDS:
        if code not in catalog:
            continue
        for kw in keywords:
            if kw in lower:
                activity_code = code
                activity_raw = kw
                break
        if activity_code:
            break

    address_raw: str | None = None
    for pattern in _ADDRESS_PATTERNS:
        match = pattern.search(text)
        if match:
            address_raw = " ".join(match.group("addr").split())
            break

    if not address_raw:
        loose = re.search(r"\ben\s+(.+?\d{1,5})\b", text, re.IGNORECASE)
        if loose:
            address_raw = " ".join(loose.group(1).split()).rstrip(".,;?")

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
            "address": address_raw,
            "confidence": 0.85 if address_raw else 0.0,
        },
        "jurisdiction": "CABA",
        "missing_fields": missing,
        "clarification_question": question,
        "status": status,
    }
