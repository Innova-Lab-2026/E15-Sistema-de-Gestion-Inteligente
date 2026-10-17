"""Golden tests: successful responses must not change while hardening the backend.

Each case calls an endpoint with deterministic providers (mock geocoder, mock epok, mock
interpreter) and compares the JSON body with tests/golden/<case>.json. Volatile fields
(generated ids and timestamps) are removed before comparing.

Regenerate on purpose only:  UPDATE_GOLDEN=1 pytest tests/test_golden_responses.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

GOLDEN_DIR = Path(__file__).with_name("golden")
VOLATILE_KEYS = {"consultation_id", "retrieved_at", "ingested_at", "published_at"}
# Filled from ORM relationships without ORDER BY: their order is not stable, compare as sets.
UNORDERED_KEYS = {"activity_codes", "source_ids"}
UPDATE = os.environ.get("UPDATE_GOLDEN") == "1"

CORRIENTES = {"latitude": -34.604, "longitude": -58.413}
CONFIRMED = {
    "normalized_address": "Avenida Corrientes 2500, CABA",
    "latitude": -34.604,
    "longitude": -58.413,
    "commune": "Comuna 5",
    "neighborhood": "Almagro",
}
# Real epok client pointing to a closed port: exercises the "epok unavailable" partial path.
EPOK_DOWN = {"epok_provider": "epok", "epok_base_url": "http://127.0.0.1:9"}

CASES: list[tuple[str, str, str, dict[str, Any] | None, dict[str, Any] | None]] = [
    # name, method, path, json body or query params, settings override
    ("health", "GET", "/health", None, None),
    ("activities", "GET", "/api/v1/activities", None, None),
    ("sources", "GET", "/api/v1/sources", None, None),
    ("offices", "GET", "/api/v1/offices", None, None),
    ("offices_filtered", "GET", "/api/v1/offices", {"category": "rubro_102", "commune": "3"}, None),
    ("open_data_packages", "GET", "/api/v1/open-data/packages", None, None),
    ("gastronomy_context", "GET", "/api/v1/open-data/gastronomy-context", {"commune": "3", "neighborhood": "Balvanera"}, None),
    ("gastronomy_context_empty", "GET", "/api/v1/open-data/gastronomy-context", {}, None),
    ("geocode_confirmed", "POST", "/api/v1/locations/geocode", {"address": "Av. Corrientes 2500"}, None),
    ("geocode_ambiguous", "POST", "/api/v1/locations/geocode", {"address": "Palermo"}, None),
    ("geocode_out_of_scope", "POST", "/api/v1/locations/geocode", {"address": "Mar del Plata"}, None),
    ("geocode_not_found", "POST", "/api/v1/locations/geocode", {"address": "Calle Inexistente 123"}, None),
    ("zoning_rubro", "POST", "/api/v1/locations/zoning", {**CORRIENTES, "activity_code": "rubro_102"}, None),
    ("zoning_no_rubro", "POST", "/api/v1/locations/zoning", CORRIENTES, None),
    ("zoning_parcel_not_found", "POST", "/api/v1/locations/zoning", {"latitude": -34.7, "longitude": -58.5}, None),
    ("interpret_cafeteria", "POST", "/api/v1/interpretations", {"query": "Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?"}, None),
    ("interpret_ropa", "POST", "/api/v1/interpretations", {"query": "Quiero abrir un local de ropa en Av. Corrientes 2500"}, None),
    ("interpret_no_address", "POST", "/api/v1/interpretations", {"query": "Quiero abrir una cafeteria"}, None),
    ("interpret_unknown_activity", "POST", "/api/v1/interpretations", {"query": "Quiero abrir una nave espacial en Av. Corrientes 2500"}, None),
    ("consultation_deterministic", "POST", "/api/v1/consultations", {"activity_code": "rubro_102", "address": "Av. Corrientes 2500"}, None),
    ("consultation_nl", "POST", "/api/v1/consultations", {"query": "Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?"}, None),
    ("consultation_nl_no_address", "POST", "/api/v1/consultations", {"query": "Quiero abrir una cafeteria"}, None),
    ("consultation_unknown_code", "POST", "/api/v1/consultations", {"activity_code": "rubro_999999", "address": "Av. Corrientes 2500"}, None),
    ("consultation_ambiguous", "POST", "/api/v1/consultations", {"activity_code": "rubro_102", "address": "Palermo"}, None),
    ("consultation_out_of_scope", "POST", "/api/v1/consultations", {"activity_code": "rubro_102", "address": "Mar del Plata"}, None),
    ("consultation_not_found", "POST", "/api/v1/consultations", {"activity_code": "rubro_102", "address": "Calle Inexistente 123"}, None),
    ("consultation_confirmed_location", "POST", "/api/v1/consultations", {"activity_code": "rubro_102", "confirmed_location": CONFIRMED}, None),
    ("consultation_non_curated", "POST", "/api/v1/consultations", {"activity_code": "rubro_309", "address": "Av. Corrientes 2500"}, None),
    ("consultation_epok_unavailable", "POST", "/api/v1/consultations", {"activity_code": "rubro_102", "address": "Av. Corrientes 2500"}, EPOK_DOWN),
]


def _normalize(value: Any, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(v, k) for k, v in value.items() if k not in VOLATILE_KEYS}
    if isinstance(value, list):
        items = [_normalize(v) for v in value]
        return sorted(items) if key in UNORDERED_KEYS else items
    return value


@pytest.mark.parametrize(
    ("name", "method", "path", "payload", "settings"),
    CASES,
    ids=[c[0] for c in CASES],
)
def test_golden_response(client, override_settings, name, method, path, payload, settings):
    if settings:
        override_settings(**settings)

    if method == "GET":
        response = client.get(path, params=payload)
    else:
        response = client.post(path, json=payload)

    assert response.status_code == 200, response.text
    body = _normalize(response.json())
    golden_file = GOLDEN_DIR / f"{name}.json"

    if UPDATE:
        golden_file.write_text(
            json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return

    assert golden_file.exists(), f"Missing golden file {golden_file.name}; run with UPDATE_GOLDEN=1"
    assert body == json.loads(golden_file.read_text(encoding="utf-8"))
