"""B24: functional and negative cases of documents/arquitectura-ia.md §17, end to end."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from app.db.data_files import barrio_por_variante, comuna_de
from app.schemas.limits import CABA_LAT_MAX, CABA_LAT_MIN, CABA_LNG_MAX, CABA_LNG_MIN

LLM = "https://llm.test/v1"
INVENTED = "INVENTADO POR EL MODELO"


def _consult(client, body: dict) -> dict:
    response = client.post("/api/v1/consultations", json=body)
    assert response.status_code == 200
    return response.json()


# --- Casos funcionales -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("query", "status", "code"),
    [
        ("Quiero abrir un local de ropa en Av. Corrientes 2500", "complete", "rubro_16"),
        ("Quiero poner una cafeteria en Palermo", "partial", "rubro_102"),  # barrio sin calle
        ("kiero abrir una farmasia en corrientes 2500", "complete", "rubro_66"),  # ortografía y minúsculas
        ("che, quiero poner un kiosko en Av. Corrientes 2500", "complete", "rubro_245"),  # coloquial
    ],
)
def test_functional_cases(client, query, status, code):
    body = _consult(client, {"query": query})
    assert body["status"] == status
    assert body["interpretation"]["activity"]["normalized_category"] == code


def test_incomplete_address_asks_for_it(client):
    body = _consult(client, {"query": "Quiero abrir una cafeteria en Corrientes"})
    assert body["reason"] == "location_missing"
    assert body["interpretation"]["activity"]["normalized_category"] == "rubro_102"


# --- Validaciones de datos ---------------------------------------------------------------------


def _inside_caba(lat: float, lon: float) -> bool:
    return CABA_LAT_MIN <= lat <= CABA_LAT_MAX and CABA_LNG_MIN <= lon <= CABA_LNG_MAX


def test_complete_answer_is_backed_by_sources(client):
    body = _consult(client, {"query": "Quiero abrir un local de ropa en Av. Corrientes 2500"})
    source_ids = {s["id"] for s in body["sources"]}
    assert body["requirements"]
    for req in body["requirements"]:
        assert req["source_ids"] and set(req["source_ids"]) <= source_ids, req["id"]
        for step in req["steps"]:
            assert step["source_ids"]
    for office in body["physical_offices"] + body["online_procedures"]:
        assert office["source_ids"]
        assert _inside_caba(office["latitude"], office["longitude"]), office["id"]
    assert _inside_caba(body["location"]["latitude"], body["location"]["longitude"])
    for source in body["sources"]:
        assert source["ingested_at"], f"{source['id']} without date"


def test_offices_commune_matches_their_barrio(client):
    for office in client.get("/api/v1/offices").json():
        barrio = barrio_por_variante(office["neighborhood"])
        if office["commune"] and barrio:
            assert str(comuna_de(barrio)) == office["commune"], office["id"]


def test_commune_and_barrio_match_the_geocoded_point(client):
    body = _consult(client, {"activity_code": "rubro_102", "address": "Cabildo 2000"})
    assert body["location"]["neighborhood_id"] == "belgrano"
    assert str(comuna_de("belgrano")) == body["location"]["commune"]


# --- Pruebas negativas -------------------------------------------------------------------------


@pytest.fixture
def llm(override_settings):
    override_settings(llm_base_url=LLM, llm_api_key="test-key")
    with respx.mock(assert_all_called=False) as mock:
        yield mock.post(f"{LLM}/chat/completions")


def test_the_model_cannot_add_requirements_offices_or_coordinates(client, llm):
    content = {
        "intent": "start_commercial_activity",
        "activity": {"raw_text": "cafeteria", "normalized_category": "rubro_102", "confidence": 0.95},
        "location": {
            "raw_text": "Av. Corrientes 2500",
            "address": "Av. Corrientes 2500",
            "confidence": 0.9,
            "latitude": 0.0,
            "longitude": 0.0,
            "commune": "99",
        },
        "jurisdiction": "CABA",
        "missing_fields": [],
        "status": "ready_for_geocoding",
        "requirements": [{"id": "req-x", "title": INVENTED, "description": INVENTED}],
        "physical_offices": [{"name": INVENTED, "latitude": 0, "longitude": 0}],
        "summary": INVENTED,
    }
    llm.mock(return_value=httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(content)}}]}))
    response = client.post("/api/v1/consultations", json={"query": "Quiero abrir una cafeteria en Av. Corrientes 2500"})
    body = response.json()

    assert body["interpretation"]["activity"]["normalized_category"] == "rubro_102"
    assert INVENTED not in response.text
    assert all(r["id"].startswith("requirement-") for r in body["requirements"])
    # Coordinates and commune come from the geocoder, not from the model.
    assert (body["location"]["latitude"], body["location"]["longitude"]) == (-34.604, -58.413)
    assert body["location"]["commune"] == "3"


def test_source_down_gives_a_clearly_informed_partial_answer(client, override_settings):
    override_settings(epok_provider="epok", epok_base_url="https://epok.test")
    with respx.mock(assert_all_called=False) as mock:
        mock.get(url__startswith="https://epok.test").mock(return_value=httpx.Response(503))
        body = _consult(client, {"activity_code": "rubro_102", "address": "Av. Corrientes 2500"})
    assert body["status"] == "partial"
    assert body["data_status"]["overall"] == "partial"
    assert "epok_unavailable" in body["data_status"]["warnings"]
    assert "zoning_epok" in body["data_status"]["missing"]
    assert body["requirements"], "what does not depend on epok is still answered"


def test_ambiguous_address_requires_confirmation_and_then_continues(client):
    blocked = _consult(client, {"activity_code": "rubro_102", "address": "Palermo"})
    assert blocked["status"] == "needs_location_confirmation"
    assert blocked["reason"] == "location_ambiguous"
    assert not blocked["requirements"] and blocked["zoning"] is None
    chosen = blocked["location"]["candidates"][0]

    confirmed = _consult(
        client,
        {
            "activity_code": "rubro_102",
            "confirmed_location": {
                "normalized_address": chosen["normalized_address"],
                "latitude": chosen["latitude"],
                "longitude": chosen["longitude"],
                "commune": chosen["commune"],
                "neighborhood": chosen["neighborhood"],
            },
        },
    )
    assert confirmed["status"] in {"complete", "partial"}
    assert confirmed["location"]["status"] == "confirmed"


@pytest.mark.parametrize(
    "body",
    [
        {"query": "cómo saco el DNI"},
        {"query": "quiero abrir una tienda de regalos en Florida 500"},
        {"activity_code": "rubro_99999", "address": "Av. Corrientes 2500"},
        {"activity_code": "rubro_102", "address": "Mar del Plata"},
    ],
    ids=["topic", "activity_not_in_catalog", "unknown_code", "outside_caba"],
)
def test_out_of_scope_never_gets_a_false_official_answer(client, body):
    data = _consult(client, body)
    assert data["status"] not in {"complete", "partial"}
    assert data["reason"]
    for block in ("requirements", "documents", "steps", "physical_offices", "online_procedures", "sources"):
        assert data[block] == [], block
    assert data["zoning"] is None
