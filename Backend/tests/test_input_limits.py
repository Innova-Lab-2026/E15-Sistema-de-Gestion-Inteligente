"""Input limits: text length, CABA coordinate bounds and request size."""

from __future__ import annotations

import pytest

from app.schemas.limits import MAX_ADDRESS_LENGTH, MAX_QUERY_LENGTH

CORRIENTES = {"latitude": -34.604, "longitude": -58.413}
CONFIRMED = {"normalized_address": "Avenida Corrientes 2500, CABA", **CORRIENTES}


def _fields(response) -> dict[str, str]:
    assert response.status_code == 422, response.text
    error = response.json()["error"]
    assert error["code"] == "invalid_request"
    return {item["field"]: item["message"] for item in error["detail"]}


@pytest.mark.parametrize(
    ("path", "payload", "field"),
    [
        ("/api/v1/interpretations", {"query": "x" * (MAX_QUERY_LENGTH + 1)}, "query"),
        ("/api/v1/consultations", {"query": "x" * (MAX_QUERY_LENGTH + 1)}, "query"),
        ("/api/v1/locations/geocode", {"address": "x" * (MAX_ADDRESS_LENGTH + 1)}, "address"),
        ("/api/v1/consultations", {"activity_code": "rubro_102", "address": "x" * (MAX_ADDRESS_LENGTH + 1)}, "address"),
        ("/api/v1/consultations", {"activity_code": "r" * 65, "address": "Av. Corrientes 2500"}, "activity_code"),
    ],
)
def test_text_too_long(client, path, payload, field):
    message = _fields(client.post(path, json=payload))[field]
    assert message.startswith("Debe tener como maximo")


def test_limit_is_inclusive(client):
    response = client.post("/api/v1/interpretations", json={"query": "x" * MAX_QUERY_LENGTH})
    assert response.status_code == 200


@pytest.mark.parametrize(
    ("latitude", "longitude", "field"),
    [
        (0.0, 0.0, "latitude"),
        (-34.604, -60.0, "longitude"),
        (-33.0, -58.413, "latitude"),
    ],
)
def test_zoning_coordinates_must_be_in_caba(client, latitude, longitude, field):
    response = client.post("/api/v1/locations/zoning", json={"latitude": latitude, "longitude": longitude})
    assert field in _fields(response)


def test_confirmed_location_must_be_in_caba(client):
    body = {"activity_code": "rubro_102", "confirmed_location": {**CONFIRMED, "latitude": 40.4}}
    assert "confirmed_location.latitude" in _fields(client.post("/api/v1/consultations", json=body))


def test_negative_epok_ids_rejected(client):
    response = client.post("/api/v1/locations/zoning", json={**CORRIENTES, "epok_rubro_id": -1})
    assert "epok_rubro_id" in _fields(response)


def test_oversized_body_rejected_before_parsing(client):
    response = client.post(
        "/api/v1/consultations",
        content=b"{" + b" " * (64 * 1024) + b"}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413
    error = response.json()["error"]
    assert error["code"] == "request_too_large"
    assert error["request_id"] == response.headers["X-Request-ID"]
