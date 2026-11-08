"""Reconocedor de direcciones sin LLM: alturas en palabras, errores de ortografía y falsos positivos."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from app.providers.address_parser import extract_address, normalize_address


@pytest.mark.parametrize(
    ("query", "address", "raw_text"),
    [
        # Alturas en palabras
        ("quiero abrir una farmacia en Monroe al mil", "Monroe 1000", "Monroe al mil"),
        ("quiero abrir una farmacia en Monroe mil quinientos", "Monroe 1500", "Monroe mil quinientos"),
        ("una farmacia en Monroe dos mil quinientos", "Monroe 2500", "Monroe dos mil quinientos"),
        ("en Santa Fe tres mil ochocientos veintisiete", "Santa Fe 3827", "Santa Fe tres mil ochocientos veintisiete"),
        ("en Corrientes setecientos treinta y cinco", "Corrientes 735", "Corrientes setecientos treinta y cinco"),
        ("Cabildo al dos mil", "Cabildo 2000", "Cabildo al dos mil"),
        # Pegadas, con guion y con errores de ortografía
        ("quiero abrir una farmacia en Monroe milquinientos", "Monroe 1500", "Monroe milquinientos"),
        ("quiero abrir una farmacia en Monroe mil-quinientos", "Monroe 1500", "Monroe mil-quinientos"),
        ("quiero abrir una farmacia en Monroe mil kinientos", "Monroe 1500", "Monroe mil kinientos"),
        ("en av. cabildo dosmil", "av. cabildo 2000", "av. cabildo dosmil"),
        ("en Rivadavia quinentos", "Rivadavia 500", "Rivadavia quinentos"),
        # Cifra por cifra y de a dos cifras
        ("quiero abrir una farmacia en calle olazabal ocho dos uno", "calle olazabal 821", "calle olazabal ocho dos uno"),
        ("en Rivadavia quince cuarenta", "Rivadavia 1540", "Rivadavia quince cuarenta"),
        # Cifras
        ("Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?", "Av. Corrientes 2500", "Av. Corrientes 2500"),
        ("quiero abrir una cafetería en avenida Corrientes al 2500", "avenida Corrientes 2500", "avenida Corrientes al 2500"),
        ("Quiero abrir una ferretería en Santiago del Estero 112", "Santiago del Estero 112", "Santiago del Estero 112"),
        ("en Av. Corrientes 2.500", "Av. Corrientes 2500", "Av. Corrientes 2.500"),
        ("en Monroe N° 1500", "Monroe 1500", "Monroe N° 1500"),
        # Cifra + "mil"
        ("quiero abrir cafeteria en Monroe al 2 mil", "Monroe 2000", "Monroe al 2 mil"),
        ("en Monroe al 2 mil 500", "Monroe 2500", "Monroe al 2 mil 500"),
        ("en Monroe 2 mil quinientos", "Monroe 2500", "Monroe 2 mil quinientos"),
        ("en Monroe 2 mil. Tengo 3 empleados", "Monroe 2000", "Monroe 2 mil"),
        ("quiero una cafeteria Monroe 1500", "Monroe 1500", "Monroe 1500"),
        # Calles con números en el nombre: el nombre no se toca
        ("en 9 de Julio 1000", "9 de Julio 1000", "9 de Julio 1000"),
        ("en Tres Arroyos quinientos", "Tres Arroyos 500", "Tres Arroyos quinientos"),
        ("en Treinta y Tres Orientales 1500", "Treinta y Tres Orientales 1500", "Treinta y Tres Orientales 1500"),
        ("en Once de Septiembre mil", "Once de Septiembre 1000", "Once de Septiembre mil"),
    ],
)
def test_extracts_address(query, address, raw_text):
    parsed = extract_address(query)

    assert parsed is not None
    assert parsed.address == address
    assert parsed.raw_text == raw_text


@pytest.mark.parametrize(
    "query",
    [
        "quiero abrir una cafetería en Palermo",
        "quiero abrir dos locales en Palermo",
        "un local de 50 metros en Palermo",
        "un local de cien m2",
        "tengo diez mil pesos para abrir en Caballito",
        "quiero abrir un negocio en el 2026",
        "quiero abrir una cafeteria a dos cuadras de Corrientes",
        "en Belgrano, tengo 3 empleados",
        "qué clima hace hoy en Buenos Aires",
        "cómo saco el DNI",
        "en Once",
        "",
    ],
)
def test_ignores_numbers_that_are_not_heights(query):
    assert extract_address(query) is None


@pytest.mark.parametrize(
    ("query", "address", "approximate"),
    [
        # Dos alturas: se usa la primera y la ubicación queda aproximada.
        ("quiero abrir cafeteria en monroe al 2 mil o 2500", "monroe 2000", True),
        ("una cafeteria en Monroe 2000 o 2500", "Monroe 2000", True),
        ("una cafeteria en Monroe dos mil u ochocientos", "Monroe 2000", True),
        # Dos direcciones distintas no son dos alturas.
        ("una cafeteria en Monroe 2500 o en Cabildo 1000", "Monroe 2500", False),
        ("una cafeteria en Monroe 2500", "Monroe 2500", False),
    ],
)
def test_two_heights_use_the_first_one(query, address, approximate):
    parsed = extract_address(query)

    assert parsed is not None
    assert (parsed.address, parsed.approximate) == (address, approximate)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Monroe dos mil quinientos", "Monroe 2500"),
        ("Monroe 2500", "Monroe 2500"),
        ("Monroe 2 mil", "Monroe 2000"),
        ("Monroe 2000 o 2500", "Monroe 2000"),
        ("Av. Corrientes 2.500", "Av. Corrientes 2.500"),
        ("Gorriti 4500, Palermo", "Gorriti 4500, Palermo"),
        ("Belgrano", "Belgrano"),
        (None, None),
    ],
)
def test_normalize_address(value, expected):
    assert normalize_address(value) == expected


def test_rules_interpreter_returns_height_in_digits(client):
    body = client.post(
        "/api/v1/interpretations",
        json={"query": "Quiero abrir una ferretería en Monroe dos mil quinientos"},
    ).json()

    assert body["provider"] == "mock"
    assert body["location"]["address"] == "Monroe 2500"
    assert body["location"]["raw_text"] == "Monroe dos mil quinientos"


def test_llm_address_in_words_is_converted(client, override_settings):
    llm_url = "https://llm.test/v1"
    override_settings(llm_base_url=llm_url, llm_api_key="test-key")
    output = {
        "intent": "start_commercial_activity",
        "activity": {"raw_text": "farmacia", "normalized_category": "rubro_66", "confidence": 0.9},
        "location": {"raw_text": "Monroe dos mil quinientos", "address": "Monroe dos mil quinientos", "confidence": 0.9},
        "jurisdiction": "CABA",
        "missing_fields": [],
        "clarification_question": None,
        "status": "ready_for_geocoding",
    }
    with respx.mock(assert_all_called=False) as mock:
        mock.post(f"{llm_url}/chat/completions").mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(output)}}]})
        )
        body = client.post(
            "/api/v1/interpretations",
            json={"query": "Quiero abrir una farmacia en Monroe dos mil quinientos"},
        ).json()

    assert body["provider"] == "llm"
    assert body["location"]["address"] == "Monroe 2500"
    assert body["location"]["raw_text"] == "Monroe dos mil quinientos"


@pytest.mark.parametrize("llm_address", ["Monroe 2 mil o 2500", "Monroe 2000", "Monroe 2500"])
def test_llm_with_two_heights_is_approximate(client, override_settings, llm_address):
    llm_url = "https://llm.test/v1"
    override_settings(llm_base_url=llm_url, llm_api_key="test-key")
    output = {
        "intent": "start_commercial_activity",
        "activity": {"raw_text": "cafeteria", "normalized_category": "rubro_102", "confidence": 0.9},
        "location": {"raw_text": llm_address, "address": llm_address, "confidence": 0.9},
        "jurisdiction": "CABA",
        "missing_fields": [],
        "status": "ready_for_geocoding",
    }
    with respx.mock(assert_all_called=False) as mock:
        mock.post(f"{llm_url}/chat/completions").mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(output)}}]})
        )
        body = client.post(
            "/api/v1/interpretations",
            json={"query": "quiero abrir cafeteria en monroe al 2 mil o 2500"},
        ).json()

    assert body["provider"] == "llm"
    assert body["location"]["address"] in {"Monroe 2000", "Monroe 2500"}
    assert body["location"]["approximate"] is True
