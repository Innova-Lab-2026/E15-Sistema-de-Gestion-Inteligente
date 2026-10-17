"""HTTP status codes of invalid requests. The error body format is covered in test_errors.py."""

from __future__ import annotations

import pytest

INVALID_REQUESTS = [
    ("geocode_empty", "/api/v1/locations/geocode", {"address": ""}),
    ("geocode_blank", "/api/v1/locations/geocode", {"address": "   "}),
    ("geocode_missing", "/api/v1/locations/geocode", {}),
    ("interpret_empty", "/api/v1/interpretations", {"query": ""}),
    ("interpret_blank", "/api/v1/interpretations", {"query": "   "}),
    ("consultation_empty", "/api/v1/consultations", {}),
    ("consultation_code_only", "/api/v1/consultations", {"activity_code": "rubro_102"}),
    ("zoning_missing_coords", "/api/v1/locations/zoning", {"activity_code": "rubro_102"}),
]


@pytest.mark.parametrize(("name", "path", "payload"), INVALID_REQUESTS, ids=[r[0] for r in INVALID_REQUESTS])
def test_invalid_request_returns_422(client, name, path, payload):
    assert client.post(path, json=payload).status_code == 422


def test_unknown_route_returns_404(client):
    assert client.get("/api/v1/nope").status_code == 404


def test_wrong_method_returns_405(client):
    assert client.get("/api/v1/consultations").status_code == 405
