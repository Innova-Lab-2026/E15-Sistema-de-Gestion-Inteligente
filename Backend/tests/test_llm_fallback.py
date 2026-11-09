"""LLM failures fall back to local rules and are reported (fallback_reason / data_status warning)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

LLM = "https://llm.test/v1"
QUERY = "Quiero abrir una cafeteria en Av. Corrientes 2500"
LLM_OK = {
    "intent": "start_commercial_activity",
    "activity": {"raw_text": "cafeteria", "normalized_category": "rubro_102", "confidence": 0.9},
    "location": {"raw_text": "Av. Corrientes 2500", "address": "Av. Corrientes 2500", "confidence": 0.9},
    "jurisdiction": "CABA",
    "missing_fields": [],
    "clarification_question": None,
    "status": "ready_for_geocoding",
}


def _completion(content) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})


@pytest.fixture
def llm(override_settings):
    override_settings(llm_base_url=LLM, llm_api_key="test-key")
    with respx.mock(assert_all_called=False) as mock:
        yield mock.post(f"{LLM}/chat/completions")


def test_valid_llm_output_is_used(client, llm):
    llm.mock(return_value=_completion(json.dumps(LLM_OK)))

    body = client.post("/api/v1/interpretations", json={"query": QUERY}).json()

    assert body["provider"] == "llm"
    assert body["fallback_reason"] is None
    assert body["activity"]["normalized_category"] == "rubro_102"
    assert llm.calls.last.request.headers["authorization"] == "Bearer test-key"


@pytest.mark.parametrize(
    ("llm_response", "reason"),
    [
        (httpx.Response(429, headers={"retry-after": "30"}), "llm_rate_limited"),
        (httpx.Response(500), "llm_unavailable"),
        (httpx.ConnectTimeout("timeout"), "llm_unavailable"),
        (httpx.Response(200, text="<html>"), "llm_invalid_output"),
        (_completion("not json"), "llm_invalid_output"),
        (_completion("[1, 2]"), "llm_invalid_output"),
        # No activity code: the validator keeps the model's status, which is not a valid literal.
        (_completion(json.dumps({**LLM_OK, "status": "whatever", "activity": {"normalized_category": None}})), "llm_invalid_output"),
        (_completion(json.dumps({**LLM_OK, "activity": {**LLM_OK["activity"], "confidence": "high"}})), "llm_invalid_output"),
    ],
    ids=["rate_limited", "http_500", "timeout", "html_body", "content_not_json", "json_array", "bad_status", "bad_confidence"],
)
def test_llm_failure_falls_back_to_rules(client, llm, llm_response, reason):
    if isinstance(llm_response, Exception):
        llm.mock(side_effect=llm_response)
    else:
        llm.mock(return_value=llm_response)

    response = client.post("/api/v1/interpretations", json={"query": QUERY})

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert body["fallback_reason"] == reason
    assert body["status"] == "ready_for_geocoding"


def test_consultation_warns_when_llm_fell_back(client, llm):
    llm.mock(return_value=httpx.Response(429))

    body = client.post("/api/v1/consultations", json={"query": QUERY}).json()

    assert body["status"] == "complete"
    assert "llm_fallback_mock" in body["data_status"]["warnings"]


def test_consultation_warns_on_blocked_responses_too(client, llm):
    llm.mock(return_value=httpx.Response(500))

    body = client.post("/api/v1/consultations", json={"query": "Quiero abrir una cafeteria"}).json()

    assert body["status"] == "needs_clarification"
    assert body["data_status"]["warnings"] == ["llm_fallback_mock"]


def test_no_warning_when_llm_is_not_configured(client):
    body = client.post("/api/v1/consultations", json={"query": QUERY}).json()
    assert "llm_fallback_mock" not in body["data_status"]["warnings"]
