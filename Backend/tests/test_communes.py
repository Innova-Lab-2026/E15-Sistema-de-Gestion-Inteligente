"""B02: the commune is a number from 1 to 15 everywhere, so communal offices match."""

from __future__ import annotations

import httpx
import pytest
import respx

from app.core.territory import normalize_commune

USIG = "https://usig.test"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Comuna 3", "3"),
        ("COMUNA 03", "3"),
        ("3", "3"),
        (3, "3"),
        (" comuna 15 ", "15"),
        ("Comuna 16", None),
        ("0", None),
        ("Palermo", None),
        ("", None),
        (None, None),
    ],
)
def test_normalize_commune(value, expected):
    assert normalize_commune(value) == expected


def _communal_offices(body: dict) -> list[dict]:
    return [o for o in body["physical_offices"] if o["id"].startswith("office-sede-")]


def test_corrientes_2500_includes_the_communal_office_of_comuna_3(client):
    body = client.post(
        "/api/v1/consultations", json={"activity_code": "rubro_102", "address": "Corrientes 2500"}
    ).json()

    assert body["location"]["commune"] == "3"
    assert body["location"]["neighborhood"] == "Balvanera"
    sedes = _communal_offices(body)
    assert sedes, "the communal office of Comuna 3 is missing"
    assert {o["commune"] for o in sedes} == {"3"}


def test_confirmed_location_with_comuna_text_matches_offices(client):
    body = client.post(
        "/api/v1/consultations",
        json={
            "activity_code": "rubro_102",
            "confirmed_location": {
                "normalized_address": "Avenida Corrientes 2500, CABA",
                "latitude": -34.604,
                "longitude": -58.413,
                "commune": "Comuna 3",
            },
        },
    ).json()

    assert body["location"]["commune"] == "3"
    assert {o["commune"] for o in _communal_offices(body)} == {"3"}


def test_usig_comuna_text_is_normalized(client, override_settings):
    override_settings(geocoder_provider="usig", geocoder_base_url=USIG, geocoder_ws_base_url=USIG)
    usig_ok = {
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
    with respx.mock(assert_all_called=False) as mock:
        mock.get(url__startswith=f"{USIG}/normalizar/").mock(return_value=httpx.Response(200, json=usig_ok))
        body = client.post("/api/v1/locations/geocode", json={"address": "Av. Corrientes 2500"}).json()

    assert body["commune"] == "3"
    assert body["candidates"][0]["commune"] == "3"


def test_offices_endpoint_accepts_comuna_text(client):
    by_number = client.get("/api/v1/offices", params={"commune": "3"}).json()
    by_text = client.get("/api/v1/offices", params={"commune": "Comuna 3"}).json()
    assert by_number and by_number == by_text
