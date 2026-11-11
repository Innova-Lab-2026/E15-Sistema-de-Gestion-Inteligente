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
        _setup.router = mock  # other USIG routes (datos_utiles) go in the same mock
        yield _setup, mock.get(url__startswith=f"{USIG}/normalizar/")


async def _hang(request):
    await asyncio.sleep(30)
    return httpx.Response(200, json=USIG_OK)


def test_usig_hanging_gives_partial_in_under_5_seconds(client, usig):
    setup, route = usig
    setup(geocoder_timeout_seconds=3, geocoder_total_timeout_seconds=4.5)  # defaults, whatever .env says
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


# B18: comuna and barrio come from a second USIG service (datos_utiles), slower than normalizar.
USIG_NO_BARRIO = {
    "direccionesNormalizadas": [
        {
            "direccion": "CABILDO AV. 2000, CABA",
            "cod_partido": "caba",
            "altura": 2000,
            "coordenadas": {"x": "-58.455896", "y": "-34.563151"},
        }
    ]
}


@pytest.fixture
def datos_utiles(usig):
    """Routes for convertir_coordenadas + datos_utiles (inside the respx mock of `usig`)."""
    router = usig[0].router
    convert = router.get(url__startswith=f"{USIG}/rest/convertir_coordenadas").mock(
        return_value=httpx.Response(200, json={"resultado": {"x": "100233.39", "y": "107811.20"}})
    )
    useful = router.get(url__startswith=f"{USIG}/datos_utiles")
    return convert, useful


def _slow(seconds: float, payload: dict):
    async def _respond(request):
        await asyncio.sleep(seconds)
        return httpx.Response(200, json=payload)

    return _respond


def test_slow_barrio_keeps_the_address_and_coordinates(client, usig, datos_utiles):
    from app.providers.geocoder import usig_state

    setup, route = usig
    setup(geocoder_total_timeout_seconds=1)
    route.mock(return_value=httpx.Response(200, json=USIG_NO_BARRIO))
    _, useful = datos_utiles
    useful.mock(side_effect=_slow(30, {"comuna": "Comuna 13", "barrio": "Belgrano"}))

    started = time.monotonic()
    body = client.post("/api/v1/locations/geocode", json={"address": "Cabildo 2000"}).json()

    assert time.monotonic() - started < 2
    assert body["status"] == "confirmed"
    assert body["normalized_address"] == "CABILDO AV. 2000, CABA"
    assert body["latitude"] == pytest.approx(-34.563151)
    assert body["commune"] is None and body["neighborhood"] is None
    # USIG answered: it is not a failure for the breaker.
    assert usig_state.failures == 0 and not usig_state.is_open


def test_address_without_barrio_is_not_cached(client, usig, datos_utiles):
    setup, route = usig
    setup(geocoder_total_timeout_seconds=1)
    route.mock(return_value=httpx.Response(200, json=USIG_NO_BARRIO))
    _, useful = datos_utiles
    useful.mock(side_effect=_slow(30, {}))
    client.post("/api/v1/locations/geocode", json={"address": "Cabildo 2000"})

    useful.mock(return_value=httpx.Response(200, json={"comuna": "Comuna 13", "barrio": "Belgrano"}))
    body = client.post("/api/v1/locations/geocode", json={"address": "Cabildo 2000"}).json()

    assert route.call_count == 2
    assert body["commune"] == "13" and body["neighborhood"] == "Belgrano"


def test_consultation_without_barrio_still_has_zoning(client, usig, datos_utiles):
    setup, route = usig
    setup(geocoder_total_timeout_seconds=1)
    route.mock(return_value=httpx.Response(200, json=USIG_NO_BARRIO))
    _, useful = datos_utiles
    useful.mock(side_effect=_slow(30, {}))

    body = client.post("/api/v1/consultations", json={"activity_code": "rubro_315", "address": "Cabildo 2000"}).json()

    assert body["status"] == "partial"
    assert body["location"]["status"] == "confirmed"
    assert body["location"]["latitude"] is not None
    assert body["zoning"] is not None
    assert "neighborhood_unavailable" in body["data_status"]["warnings"]
    assert "geocoder_unavailable" not in body["data_status"]["warnings"]


def test_slow_normalizar_is_still_unavailable(client, usig):
    from app.providers.geocoder import usig_state

    setup, route = usig
    setup(geocoder_total_timeout_seconds=1)
    route.mock(side_effect=_slow(30, USIG_OK))

    body = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"}).json()

    assert body["status"] == "unavailable"
    assert usig_state.failures == 1


def test_candidates_get_their_barrio_at_the_same_time(client, usig, datos_utiles):
    """Two CABA matches: comuna/barrio are looked up in parallel, so both fit in the time left."""
    setup, route = usig
    setup(geocoder_total_timeout_seconds=1.5)
    item = USIG_NO_BARRIO["direccionesNormalizadas"][0]
    route.mock(return_value=httpx.Response(200, json={"direccionesNormalizadas": [item, {**item, "direccion": "CABILDO 2000, CABA"}]}))
    _, useful = datos_utiles
    useful.mock(side_effect=_slow(0.8, {"comuna": "Comuna 13", "barrio": "Belgrano"}))

    body = client.post("/api/v1/locations/geocode", json={"address": "Cabildo 2000"}).json()

    assert body["status"] == "ambiguous"
    assert [c["neighborhood"] for c in body["candidates"]] == ["Belgrano", "Belgrano"]
