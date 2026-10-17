"""Per-client rate limit on the endpoints that call external services."""

from __future__ import annotations

import pytest

from app.core.rate_limit import WINDOW_SECONDS, SlidingWindowLimiter, limiter

GEOCODE = ("/api/v1/locations/geocode", {"address": "Av. Corrientes 2500"})


@pytest.fixture
def limited(override_settings):
    limiter.reset()
    override_settings(rate_limit_enabled=True, rate_limit_per_minute=3)
    yield
    limiter.reset()


def test_over_limit_returns_429_with_retry_after(client, limited):
    path, body = GEOCODE
    for _ in range(3):
        assert client.post(path, json=body).status_code == 200

    response = client.post(path, json=body)

    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60
    error = response.json()["error"]
    assert error["code"] == "rate_limited"
    assert error["detail"] == {"limit_per_minute": 3}


def test_limit_is_shared_across_external_endpoints(client, limited):
    client.post(GEOCODE[0], json=GEOCODE[1])
    client.post("/api/v1/interpretations", json={"query": "Quiero abrir una cafeteria"})
    client.post("/api/v1/consultations", json={"activity_code": "rubro_102", "address": "Av. Corrientes 2500"})

    assert client.post("/api/v1/locations/zoning", json={"latitude": -34.604, "longitude": -58.413}).status_code == 429


def test_catalog_and_health_are_not_limited(client, limited):
    for _ in range(5):
        assert client.get("/api/v1/activities").status_code == 200
        assert client.get("/health").status_code == 200


def test_disabled_by_setting(client, override_settings):
    limiter.reset()
    override_settings(rate_limit_enabled=False, rate_limit_per_minute=1)
    for _ in range(3):
        assert client.post(GEOCODE[0], json=GEOCODE[1]).status_code == 200


def test_window_slides():
    window = SlidingWindowLimiter()
    assert window.hit("ip", 2, now=0.0) is None
    assert window.hit("ip", 2, now=10.0) is None
    assert window.hit("ip", 2, now=20.0) == pytest.approx(40.0)
    assert window.hit("ip", 2, now=WINDOW_SECONDS + 0.1) is None  # first hit expired
    assert window.hit("other", 2, now=20.0) is None  # per client
