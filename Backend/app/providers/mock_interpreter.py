"""Rule-based interpreter for local tests without an LLM key.

Orden: 1) dirección (`address_parser`), 2) barrio (`neighborhood_parser`), 3) rubro en el texto
que queda, con palabras completas: así "Retiro" no da "tiro", "botica" no da "tic" y
"Flores" (el barrio) no da Vivero.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from app.db.catalog_data import ACTIVITY_DEFINITIONS, activity_synonyms
from app.db.data_files import fold
from app.providers.address_parser import extract_address
from app.providers.neighborhood_parser import find_neighborhood

# Palabras de los nombres oficiales que no sirven para elegir un rubro: lugares, palabras de
# todos los días o demasiado generales. Son la causa de la mayoría de los falsos positivos.
_NAME_TOKEN_STOPWORDS = {
    "buenos", "aires", "ciudad", "barrio", "parque", "villa", "puerto", "alto", "bajo", "centro",
    "casa", "general", "especial", "publico", "publica", "nivel", "clase", "tipo", "otro", "otra",
    "similares", "excepto", "excluido", "incluido", "principal", "comercial", "comercio",
    "minorista", "mayorista", "establecimiento", "establecimientos", "servicio", "local",
    "venta", "ventas", "hasta", "superior", "estandar", "categoria", "metros", "cuadrados",
}
# Una palabra que aparece en tres o más nombres oficiales no identifica un rubro.
_NAME_TOKEN_MAX_RUBROS = 2
_NAME_TOKEN_MIN_LENGTH = 5


@lru_cache
def name_token_index() -> dict[str, tuple[str, ...]]:
    """Palabra plegada de los nombres oficiales -> rubros cuyo nombre la tiene (uno o dos)."""
    per_code = {code: {fold(k) for k in keywords} for code, _n, _e, _c, _r, keywords in ACTIVITY_DEFINITIONS}
    owners: dict[str, list[str]] = {}
    for code, tokens in per_code.items():
        for token in tokens:
            owners.setdefault(token, []).append(code)
    return {
        token: tuple(codes)
        for token, codes in owners.items()
        if len(token) >= _NAME_TOKEN_MIN_LENGTH
        and " " not in token
        and token not in _NAME_TOKEN_STOPWORDS
        and len(codes) <= _NAME_TOKEN_MAX_RUBROS
    }


@lru_cache
def _name_tokens() -> list[tuple[str, str]]:
    """(palabra plegada, rubro_code), las más largas primero."""
    pairs = [(token, code) for token, codes in name_token_index().items() for code in codes]
    return sorted(pairs, key=lambda item: (-len(item[0]), item[1]))


@lru_cache(maxsize=4096)
def _word_pattern(term: str) -> re.Pattern[str]:
    # Palabra completa, admite plural ("kioscos", "farmacias").
    return re.compile(rf"(?<![a-z0-9]){re.escape(term)}(?:s|es)?(?![a-z0-9])")


def _synonyms_longest_first() -> list[tuple[str, str]]:
    return sorted(activity_synonyms().items(), key=lambda item: -len(item[0]))


def find_activity(text: str, catalog: dict[str, str]) -> tuple[str, str, str] | None:
    """(rubro_code, término encontrado, "synonym" | "name"). Sinónimos primero, el más largo gana."""
    folded = fold(text)
    for term, code in _synonyms_longest_first():
        if code in catalog and _word_pattern(term).search(folded):
            return code, term, "synonym"
    for token, code in _name_tokens():
        if code in catalog and _word_pattern(token).search(folded):
            return code, token, "name"
    return None


def without(text: str, spans: list[tuple[int, int]]) -> str:
    """El texto con esos tramos reemplazados por una coma (corta palabras, no las junta)."""
    out, last = [], 0
    for start, end in sorted(spans):
        out.append(text[last:start])
        out.append(" , ")
        last = end
    out.append(text[last:])
    return "".join(out)


def _literal(text: str, folded_term: str) -> str | None:
    """El término tal como lo escribió la persona ("cafetería"), para `activity.raw_text`."""
    for match in re.finditer(r"[^\W_]+(?:\s+[^\W_]+)*", text):
        words = list(re.finditer(r"[^\W_]+", match.group()))
        n = len(folded_term.split())
        for i in range(len(words) - n + 1):
            chunk = match.group()[words[i].start() : words[i + n - 1].end()]
            if _word_pattern(folded_term).fullmatch(fold(chunk)):
                return chunk
    return None


def location_spans(text: str) -> list[tuple[int, int]]:
    """Tramos de la dirección y del barrio: se sacan del texto antes de buscar el rubro."""
    parsed = extract_address(text)
    spans = [(parsed.start, parsed.end)] if parsed else []
    neighborhood = find_neighborhood(text, skip=spans)
    if neighborhood:
        spans.append((neighborhood.start, neighborhood.end))
    return spans


def mock_interpret(query: str, catalog: dict[str, str]) -> dict[str, Any]:
    """Return a raw interpretation dict (pre-validation). catalog: code -> display_name."""
    text = query.strip()

    parsed = extract_address(text)
    spans = location_spans(text)

    found = find_activity(without(text, spans), catalog)
    activity_code = found[0] if found else None
    activity_raw = (_literal(text, found[1]) or found[1]) if found else None

    address_raw = parsed.raw_text if parsed else None
    address = parsed.address if parsed else None

    intent = "start_commercial_activity" if activity_code else None
    missing: list[str] = []
    if not activity_code:
        missing.append("activity")
    if not address_raw:
        missing.append("location")

    if activity_code and address_raw:
        status = "ready_for_geocoding"
    elif address_raw and not activity_code:
        status = "activity_unknown"
    else:
        status = "needs_clarification"

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
        "clarification_question": None,
        "status": status,
    }
