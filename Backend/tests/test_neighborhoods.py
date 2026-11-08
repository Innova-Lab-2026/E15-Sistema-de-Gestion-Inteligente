"""B07: the barrio named in the query is part of the interpretation and gives a partial answer."""

from __future__ import annotations

import json

import httpx
import respx


def _interpret(client, query: str) -> dict:
    return client.post("/api/v1/interpretations", json={"query": query}).json()


def test_interpretation_reports_the_barrio(client):
    body = _interpret(client, "quiero poner una barbería en Belgrano")
    assert body["activity"]["normalized_category"] == "rubro_315"
    location = body["location"]
    assert (location["neighborhood_id"], location["neighborhood"], location["commune"]) == ("belgrano", "Belgrano", "13")
    assert location["address"] is None
    assert body["missing_fields"] == ["address"]
    assert body["status"] == "needs_clarification"


def test_barrio_and_street_together(client):
    for query in ("quiero abrir una cafetería en Gorriti 4500, Palermo", "quiero abrir una cafetería en Palermo, Gorriti 4500"):
        location = _interpret(client, query)["location"]
        assert location["address"] == "Gorriti 4500", query
        assert location["neighborhood_id"] == "palermo", query


def test_peluqueria_en_belgrano_is_partial_with_communal_office(client):
    response = client.post("/api/v1/consultations", json={"query": "Peluquería en Belgrano"})
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "partial"
    assert body["reason"] == "location_neighborhood_only"
    assert body["location"]["status"] == "neighborhood"
    assert body["location"]["neighborhood_id"] == "belgrano"
    assert body["location"]["commune"] == "13"
    assert body["zoning"] is None
    assert body["requirements"]
    assert "address" in body["data_status"]["missing"]
    sedes = [o for o in body["physical_offices"] if o["id"].startswith("office-sede-")]
    assert sedes and {o["commune"] for o in sedes} == {"13"}
    assert "calle y altura" in body["message"]


def test_deterministic_consultation_by_neighborhood(client):
    body = client.post("/api/v1/consultations", json={"activity_code": "rubro_315", "neighborhood_id": "belgrano"}).json()
    assert body["status"] == "partial"
    assert body["reason"] == "location_neighborhood_only"


def test_geocoded_location_has_neighborhood_id(client):
    body = client.post("/api/v1/consultations", json={"activity_code": "rubro_102", "address": "Av. Corrientes 2500"}).json()
    assert body["location"]["neighborhood_id"] == "balvanera"


def test_llm_address_that_is_only_a_barrio(client, override_settings):
    override_settings(llm_base_url="https://llm.test/v1", llm_api_key="test-key")
    content = {
        "intent": "start_commercial_activity",
        "activity": {"raw_text": "barbería", "normalized_category": "rubro_315", "confidence": 0.9},
        "location": {"raw_text": "Belgrano", "address": "Belgrano", "confidence": 0.8},
        "jurisdiction": "CABA",
        "missing_fields": [],
        "clarification_question": None,
        "status": "ready_for_geocoding",
    }
    completion = httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(content)}}]})
    with respx.mock(assert_all_called=False) as mock:
        mock.post("https://llm.test/v1/chat/completions").mock(return_value=completion)
        body = _interpret(client, "quiero poner una barbería en Belgrano")
    assert body["provider"] == "llm"
    assert body["location"]["address"] is None
    assert body["location"]["neighborhood_id"] == "belgrano"
    assert body["status"] == "needs_clarification"
