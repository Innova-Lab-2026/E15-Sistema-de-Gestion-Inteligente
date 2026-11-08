"""B27: corners ("Corrientes y Callao"), "entre calles" and barrio + street together."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import respx

from app.providers.address_parser import extract_address

USIG = "https://usig.test"


@pytest.mark.parametrize(
    ("query", "address", "raw_text", "approximate"),
    [
        ("quiero abrir un kiosco en Corrientes y Callao", "Corrientes y Callao", "Corrientes y Callao", False),
        ("en Corrientes esquina Callao", "Corrientes y Callao", "Corrientes esquina Callao", False),
        ("en Corrientes esq. Callao", "Corrientes y Callao", "Corrientes esq. Callao", False),
        ("en la esquina de Corrientes y Callao", "Corrientes y Callao", "Corrientes y Callao", False),
        ("en Av. Corrientes esq. Av. Callao", "Av. Corrientes y Av. Callao", "Av. Corrientes esq. Av. Callao", False),
        ("una cafeteria en Santa Fe y Coronel Diaz", "Santa Fe y Coronel Diaz", "Santa Fe y Coronel Diaz", False),
        (
            "un kiosco en Corrientes entre Callao y Riobamba",
            "Corrientes y Callao",
            "Corrientes entre Callao y Riobamba",
            True,
        ),
    ],
)
def test_corners(query, address, raw_text, approximate):
    parsed = extract_address(query)
    assert parsed is not None
    assert (parsed.address, parsed.raw_text, parsed.approximate) == (address, raw_text, approximate)


@pytest.mark.parametrize(
    "query",
    [
        "quiero abrir un local en Corrientes y tengo dos empleados",
        "quiero abrir un kiosco en Palermo y Belgrano",  # dos barrios, no una esquina
        "kiosco y almacen en Flores",
        "quiero abrir un local en Caballito",
    ],
)
def test_and_that_is_not_a_corner(query):
    assert extract_address(query) is None


def test_street_number_wins_over_corner():
    assert extract_address("en Corrientes 2500 y Callao").address == "Corrientes 2500"


def test_corner_consultation_with_mock(client):
    body = client.post("/api/v1/consultations", json={"query": "quiero abrir un kiosco en Corrientes y Callao"}).json()
    assert body["location"]["status"] == "confirmed"
    assert body["location"]["precision"] == "intersection"
    assert "address_approximate" not in body["data_status"]["warnings"]


def test_between_streets_is_approximate(client):
    interpretation = client.post(
        "/api/v1/interpretations", json={"query": "un kiosco en Corrientes entre Callao y Riobamba"}
    ).json()
    assert interpretation["location"]["address"] == "Corrientes y Callao"
    assert interpretation["location"]["approximate"] is True

    body = client.post("/api/v1/consultations", json={"query": "un kiosco en Corrientes entre Callao y Riobamba"}).json()
    assert "address_approximate" in body["data_status"]["warnings"]


def test_corner_reaches_usig_as_intersection(client, override_settings):
    override_settings(geocoder_provider="usig", geocoder_base_url=USIG, geocoder_ws_base_url=USIG)
    usig_ok = {
        "direccionesNormalizadas": [
            {
                "direccion": "CORRIENTES AV. y CALLAO AV., CABA",
                "cod_partido": "caba",
                "tipo": "calle_y_calle",
                "coordenadas": {"x": "-58.3922", "y": "-34.6043"},
                "nombre_comuna": "Comuna 1",
                "nombre_barrio": "San Nicolas",
            }
        ]
    }
    with respx.mock(assert_all_called=False) as mock:
        route = mock.get(url__startswith=f"{USIG}/normalizar/").mock(return_value=httpx.Response(200, json=usig_ok))
        body = client.post(
            "/api/v1/consultations", json={"query": "quiero abrir un kiosco en Corrientes esquina Callao"}
        ).json()

    sent = parse_qs(urlparse(str(route.calls.last.request.url)).query)["direccion"]
    assert sent == ["Corrientes y Callao"]
    assert body["location"]["precision"] == "intersection"


def test_two_heights_are_approximate(client):
    query = "quiero abrir un kiosco en Corrientes al 2 mil 500 o 2600"
    interpretation = client.post("/api/v1/interpretations", json={"query": query}).json()
    assert interpretation["location"]["address"] == "Corrientes 2500"
    assert interpretation["location"]["approximate"] is True

    body = client.post("/api/v1/consultations", json={"query": query}).json()
    assert "address_approximate" in body["data_status"]["warnings"]
