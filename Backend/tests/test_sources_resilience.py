"""Official sources failing: typed statuses and partial consultations instead of 500s.

USIG and epok are simulated at the HTTP level with respx (no network).
"""

from __future__ import annotations

import httpx
import pytest
import respx

USIG = "https://usig.test"
USIG_WS = "https://ws-usig.test"
EPOK = "https://epok.test"
USER_AGENT = "Mozilla/5.0 (compatible; InobaLab-TECBA/1.0)"
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
    override_settings(geocoder_provider="usig", geocoder_base_url=USIG, geocoder_ws_base_url=USIG_WS)
    with respx.mock(assert_all_called=False) as mock:
        yield mock.get(url__startswith=f"{USIG}/normalizar/")


@pytest.mark.parametrize(
    "failure",
    [
        httpx.Response(503),
        httpx.Response(200, text="<html>Request Rejected</html>"),
        httpx.Response(200, json=["unexpected"]),
        httpx.ConnectTimeout("timeout"),
    ],
    ids=["http_503", "waf_html", "unexpected_json", "timeout"],
)
def test_geocode_reports_unavailable(client, usig, failure):
    if isinstance(failure, Exception):
        usig.mock(side_effect=failure)
    else:
        usig.mock(return_value=failure)

    response = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["latitude"] is None
    assert "USIG" in body["message"]


def test_consultation_is_partial_when_usig_fails(client, usig):
    usig.mock(return_value=httpx.Response(500))

    response = client.post("/api/v1/consultations", json=CONSULTATION)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "partial"
    assert body["location"]["status"] == "unavailable"
    assert body["data_status"] == {
        "overall": "partial",
        "missing": ["location"],
        "warnings": ["geocoder_unavailable"],
    }
    assert body["zoning"] is None
    assert body["requirements"], "requirements do not depend on the location"
    assert body["sources"]


def test_usig_requests_send_user_agent(client, usig, override_settings):
    usig.mock(return_value=httpx.Response(200, json=USIG_OK))

    response = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"})

    assert response.json()["status"] == "confirmed"
    assert usig.calls.last.request.headers["user-agent"] == USER_AGENT


def test_epok_failure_does_not_leak_internals(client, override_settings):
    override_settings(epok_provider="epok", epok_base_url=EPOK)
    with respx.mock(assert_all_called=False) as mock:
        route = mock.get(url__startswith=EPOK).mock(return_value=httpx.Response(500))
        response = client.post(
            "/api/v1/locations/zoning",
            json={"latitude": -34.604, "longitude": -58.413, "activity_code": "rubro_102"},
        )

    body = response.json()
    assert body["status"] == "unavailable"
    assert body["message"] == "Ciudad 3D / epok no esta disponible en este momento."
    assert EPOK not in response.text
    assert route.calls.last.request.headers["user-agent"] == USER_AGENT
