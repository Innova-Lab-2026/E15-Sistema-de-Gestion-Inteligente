"""B18: USIG timeouts, short cache and pause after consecutive failures."""

from __future__ import annotations

import asyncio
import time

import httpx
import pytest
import respx

USIG = "https://usig.test"
CONSULTATION = {"activity_code": "rubro_102", "address": "Av. Corrientes 2500"}
USIG_OK = {
    "direccionesNormalizadas": [
        {
            "direccion": "CORRIENTES AV. 2500, CABA",
            "cod_partido": "caba",
            "altura": 2500,
            "coordenadas": {"x": "-58.402", "y": "-34.6048"},
            "nombre_comuna": "Comuna 3",
            "nombre_barrio": "Balvanera",
        }
    ]
}


@pytest.fixture
def usig(override_settings):
    def _setup(**changes):
        override_settings(geocoder_provider="usig", geocoder_base_url=USIG, geocoder_ws_base_url=USIG, **changes)

    with respx.mock(assert_all_called=False) as mock:
        yield _setup, mock.get(url__startswith=f"{USIG}/normalizar/")


async def _hang(request):
    await asyncio.sleep(30)
    return httpx.Response(200, json=USIG_OK)


def test_usig_hanging_gives_partial_in_under_5_seconds(client, usig):
    setup, route = usig
    setup()  # default timeouts
    route.mock(side_effect=_hang)

    started = time.monotonic()
    body = client.post("/api/v1/consultations", json=CONSULTATION).json()
    elapsed = time.monotonic() - started

    assert body["status"] == "partial"
    assert body["location"]["status"] == "unavailable"
    assert elapsed < 5, f"took {elapsed:.1f} s"


def test_after_consecutive_failures_usig_is_not_called(client, usig):
    setup, route = usig
    setup(geocoder_breaker_failures=3, geocoder_breaker_cooldown_seconds=60)
    route.mock(return_value=httpx.Response(503))

    for _ in range(3):
        assert client.post("/api/v1/consultations", json=CONSULTATION).json()["status"] == "partial"
    calls = route.call_count

    started = time.monotonic()
    body = client.post("/api/v1/consultations", json=CONSULTATION).json()
    assert body["location"]["status"] == "unavailable"
    assert route.call_count == calls, "the breaker is open: USIG must not be called"
    assert time.monotonic() - started < 1


def test_breaker_closes_after_cooldown(client, usig):
    from app.providers.geocoder import usig_state

    setup, route = usig
    setup(geocoder_breaker_failures=1, geocoder_breaker_cooldown_seconds=60)
    route.mock(return_value=httpx.Response(503))
    client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})
    assert usig_state.is_open

    usig_state.open_until = 0  # cooldown over
    route.mock(return_value=httpx.Response(200, json=USIG_OK))
    body = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"}).json()
    assert body["status"] == "confirmed"
    assert not usig_state.is_open


def test_resolved_addresses_are_cached(client, usig):
    setup, route = usig
    setup()
    route.mock(return_value=httpx.Response(200, json=USIG_OK))

    first = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"}).json()
    second = client.post("/api/v1/locations/geocode", json={"address": "av. corrientes   2500"}).json()

    assert first["status"] == second["status"] == "confirmed"
    assert route.call_count == 1
    assert second["original_address"] == "av. corrientes   2500"


def test_failures_are_not_cached(client, usig):
    setup, route = usig
    setup()
    route.mock(return_value=httpx.Response(503))
    client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})
    route.mock(return_value=httpx.Response(200, json=USIG_OK))
    body = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"}).json()
    assert body["status"] == "confirmed"


def test_cache_can_be_disabled(client, usig):
    setup, route = usig
    setup(geocoder_cache_ttl_seconds=0)
    route.mock(return_value=httpx.Response(200, json=USIG_OK))
    client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})
    client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})
    assert route.call_count == 2
