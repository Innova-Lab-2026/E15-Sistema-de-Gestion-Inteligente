"""Single error format, request id and global exception wrapper (app/core/errors.py)."""

from __future__ import annotations

import pytest

from app.core.errors import AppError, ErrorCode
from app.services.location import LocationService

CORS_ORIGIN = "http://localhost:3000"


def _error(response) -> dict:
    body = response.json()
    assert set(body) == {"error"}
    error = body["error"]
    assert set(error) == {"code", "message", "detail", "request_id"}
    assert error["request_id"] == response.headers["X-Request-ID"]
    assert error["message"]
    return error


def test_validation_error_in_spanish(client):
    response = client.post("/api/v1/locations/geocode", json={})
    assert response.status_code == 422
    error = _error(response)
    assert error["code"] == "invalid_request"
    assert error["detail"] == [{"field": "address", "message": "Campo obligatorio."}]


def test_blank_field_uses_same_format(client):
    response = client.post("/api/v1/interpretations", json={"query": "   "})
    assert response.status_code == 422
    assert _error(response)["detail"] == [{"field": "query", "message": "Campo obligatorio."}]


def test_model_validator_message_is_kept(client):
    response = client.post("/api/v1/consultations", json={"activity_code": "rubro_102"})
    assert response.status_code == 422
    (item,) = _error(response)["detail"]
    assert item["field"] is None
    assert "activity_code + address" in item["message"]


def test_invalid_json_body(client):
    response = client.post(
        "/api/v1/consultations",
        content="{not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert _error(response)["code"] == "invalid_request"


@pytest.mark.parametrize(
    ("method", "path", "status", "code"),
    [
        ("GET", "/api/v1/nope", 404, "not_found"),
        ("GET", "/api/v1/consultations", 405, "method_not_allowed"),
    ],
)
def test_routing_errors(client, method, path, status, code):
    response = client.request(method, path)
    assert response.status_code == status
    error = _error(response)
    assert error["code"] == code
    assert error["detail"] is None


def test_unhandled_exception_returns_controlled_500(client, monkeypatch):
    async def boom(self, address):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(LocationService, "geocode", boom)
    response = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})
    assert response.status_code == 500
    error = _error(response)
    assert error["code"] == "internal_error"
    assert "secret" not in response.text

    # The server keeps serving after the failure.
    assert client.get("/health").status_code == 200


def test_app_error_from_a_service(client, monkeypatch):
    async def fail(self, address):
        raise AppError(ErrorCode.NOT_FOUND, "x", headers={"Retry-After": "5"})

    monkeypatch.setattr(LocationService, "geocode", fail)
    response = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})
    assert response.status_code == 404
    assert response.headers["Retry-After"] == "5"
    error = _error(response)
    assert (error["code"], error["detail"]) == ("not_found", "x")


def test_request_id_is_generated_and_echoed(client):
    generated = client.get("/health").headers["X-Request-ID"]
    assert len(generated) == 12
    assert client.get("/health", headers={"X-Request-ID": "front-123"}).headers["X-Request-ID"] == "front-123"


def test_client_request_id_is_bounded(client):
    response = client.get("/health", headers={"X-Request-ID": "a" * 500})
    assert response.headers["X-Request-ID"] == "a" * 64


def test_error_responses_keep_cors_headers(client):
    response = client.post("/api/v1/locations/geocode", json={}, headers={"Origin": CORS_ORIGIN})
    assert response.status_code == 422
    assert response.headers["access-control-allow-origin"] == CORS_ORIGIN


def test_openapi_documents_error_contract(client):
    spec = client.get("/openapi.json").json()
    responses = spec["paths"]["/api/v1/consultations"]["post"]["responses"]
    assert responses["422"]["content"]["application/json"]["schema"]["$ref"].endswith("/ErrorResponse")
    assert "500" in responses
