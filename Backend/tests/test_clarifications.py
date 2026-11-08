"""B09: normalized clarifications. Fixed `reason` and `missing_fields`, partial interpretation
always returned, and no text written by the LLM in any response."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from app.schemas.interpretation import Reason

LLM = "https://llm.test/v1"
LLM_TEXT = "TEXTO LIBRE DEL MODELO"

# (body for /consultations, expected status, expected reason)
CONSULTATION_CASES = [
    ({"query": "quiero abrir un negocio"}, "needs_clarification", "activity_missing"),
    ({"activity_code": "rubro_99999", "address": "Av. Corrientes 2500"}, "activity_unknown", "activity_not_in_catalog"),
    ({"query": "quiero abrir una cafeteria"}, "needs_clarification", "location_missing"),
    ({"query": "quiero abrir una cafeteria en Palermo"}, "partial", "location_neighborhood_only"),
    ({"activity_code": "rubro_102", "address": "Calle Inexistente 123"}, "location_not_found", "location_not_found"),
    ({"activity_code": "rubro_102", "address": "San Martin 100"}, "needs_location_confirmation", "location_ambiguous"),
    ({"activity_code": "rubro_102", "address": "Mar del Plata"}, "out_of_scope", "location_outside_caba"),
    ({"query": "cómo saco el DNI"}, "out_of_scope", "topic_out_of_scope"),
]


def test_every_reason_has_a_case():
    assert {reason for *_, reason in CONSULTATION_CASES} == set(Reason.__args__)


@pytest.mark.parametrize(("body", "status", "reason"), CONSULTATION_CASES, ids=[c[2] for c in CONSULTATION_CASES])
def test_consultation_reason(client, body, status, reason):
    response = client.post("/api/v1/consultations", json=body)
    assert response.status_code == 200
    data = response.json()
    assert (data["status"], data["reason"]) == (status, reason)


def test_complete_consultation_has_no_reason(client):
    data = client.post("/api/v1/consultations", json={"query": "Quiero abrir una cafeteria en Av. Corrientes 2500"}).json()
    assert data["status"] == "complete"
    assert data["reason"] is None


@pytest.mark.parametrize(
    ("query", "status", "reason", "missing"),
    [
        ("quiero abrir un negocio", "needs_clarification", "activity_missing", ["activity", "location"]),
        ("quiero abrir algo en Av. Corrientes 2500", "activity_unknown", "activity_missing", ["activity"]),
        ("quiero abrir una cafeteria", "needs_clarification", "location_missing", ["location"]),
        ("quiero abrir una cafeteria en Palermo", "needs_clarification", "location_neighborhood_only", ["address"]),
        ("qué clima hace hoy en Buenos Aires", "out_of_scope", "topic_out_of_scope", ["activity", "location"]),
        ("Quiero abrir una cafeteria en Av. Corrientes 2500", "ready_for_geocoding", None, []),
    ],
)
def test_interpretation_reason(client, query, status, reason, missing):
    data = client.post("/api/v1/interpretations", json={"query": query}).json()
    assert (data["status"], data["reason"]) == (status, reason)
    assert data["missing_fields"] == missing
    assert "clarification_question" not in data


def test_blocked_consultation_keeps_the_partial_interpretation(client):
    data = client.post("/api/v1/consultations", json={"query": "quiero abrir algo en Av. Corrientes 2500"}).json()
    assert data["status"] == "activity_unknown"
    assert data["interpretation"] is not None
    assert data["interpretation"]["location"]["address"] == "Av. Corrientes 2500"
    assert data["interpretation"]["missing_fields"] == ["activity"]

    data = client.post("/api/v1/consultations", json={"query": "quiero abrir una cafeteria"}).json()
    assert data["interpretation"]["activity"]["normalized_category"] == "rubro_102"


@pytest.fixture
def llm(override_settings):
    override_settings(llm_base_url=LLM, llm_api_key="test-key")
    with respx.mock(assert_all_called=False) as mock:
        yield mock.post(f"{LLM}/chat/completions")


def _llm_answer(**overrides) -> httpx.Response:
    content = {
        "intent": "start_commercial_activity",
        "activity": {"raw_text": "un emprendimiento gastronómico", "normalized_category": None, "confidence": 0.4},
        "location": {"raw_text": None, "address": None, "confidence": 0.0},
        "jurisdiction": "CABA",
        "missing_fields": ["actividad", "direccion"],
        "clarification_question": LLM_TEXT,
        "status": "needs_clarification",
        **overrides,
    }
    return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(content)}}]})


@pytest.mark.parametrize("path", ["/api/v1/interpretations", "/api/v1/consultations"])
def test_no_llm_text_in_responses(client, llm, path):
    llm.mock(return_value=_llm_answer())
    response = client.post(path, json={"query": "quiero abrir una cafetería"})
    assert response.status_code == 200
    assert LLM_TEXT not in response.text
    # The model paraphrased the activity: raw_text is dropped. Its free-form missing_fields too.
    assert "emprendimiento" not in response.text
    assert "direccion" not in response.text


def test_llm_code_outside_catalog_is_activity_not_in_catalog(client, llm):
    llm.mock(
        return_value=_llm_answer(
            activity={"raw_text": "tienda de regalos", "normalized_category": "rubro_inventado", "confidence": 0.9},
            location={"raw_text": "Florida 500", "address": "Florida 500", "confidence": 0.9},
            status="ready_for_geocoding",
        )
    )
    data = client.post("/api/v1/interpretations", json={"query": "quiero abrir una tienda de regalos en Florida 500"}).json()
    assert data["provider"] == "llm"
    assert data["activity"]["normalized_category"] is None
    assert data["activity"]["raw_text"] == "tienda de regalos"
    assert data["reason"] == "activity_not_in_catalog"
    assert "rubro_inventado" not in json.dumps(data)


def test_synonym_rescues_an_invented_llm_code(client, llm):
    llm.mock(
        return_value=_llm_answer(
            activity={"raw_text": "cafetería", "normalized_category": "rubro_inventado", "confidence": 0.9},
            location={"raw_text": "Av. Corrientes 2500", "address": "Av. Corrientes 2500", "confidence": 0.9},
            status="ready_for_geocoding",
        )
    )
    data = client.post("/api/v1/interpretations", json={"query": "quiero abrir una cafetería en Av. Corrientes 2500"}).json()
    assert data["activity"]["normalized_category"] == "rubro_102"
    assert data["activity_candidates"][0]["match"] == "synonym"
    assert data["reason"] is None
