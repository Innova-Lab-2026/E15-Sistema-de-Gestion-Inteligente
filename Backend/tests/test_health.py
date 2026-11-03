"""Liveness (/health), readiness (/ready) and CORS defaults."""

from __future__ import annotations

from sqlalchemy.exc import OperationalError

from app.db.session import get_db


def test_ready_when_database_answers(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_not_ready_when_database_fails(client, app):
    class BrokenSession:
        async def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    async def broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = broken_db
    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "database_unavailable"
    assert "connection refused" not in response.text
    # Liveness does not depend on the database.
    assert client.get("/health").status_code == 200


def test_cors_allows_vite_origin_without_credentials(client):
    response = client.options(
        "/api/v1/consultations",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-credentials" not in response.headers


def test_cors_rejects_unknown_origin(client):
    response = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers
