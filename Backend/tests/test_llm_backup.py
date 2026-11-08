"""B17: LLM chain main -> backup (OpenRouter) -> local rules."""

from __future__ import annotations

import json
import logging

import httpx
import pytest
import respx

MAIN = "https://gemini.test/v1"
BACKUP = "https://openrouter.test/api/v1"
QUERY = "Quiero abrir una cafeteria en Av. Corrientes 2500"
OK = {
    "intent": "start_commercial_activity",
    "activity": {"raw_text": "cafeteria", "normalized_category": "rubro_102", "confidence": 0.9},
    "activity_candidates": ["rubro_102"],
    "location": {"raw_text": "Av. Corrientes 2500", "address": "Av. Corrientes 2500", "confidence": 0.9},
    "jurisdiction": "CABA",
    "missing_fields": [],
    "status": "ready_for_geocoding",
}


def _completion() -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(OK)}}]})


@pytest.fixture
def providers(override_settings):
    override_settings(
        llm_base_url=MAIN,
        llm_api_key="main-key",
        llm_model="gemini-flash-lite-latest",
        llm_fallback_base_url=BACKUP,
        llm_fallback_api_key="backup-key",
        llm_fallback_model="some-model:free",
    )
    with respx.mock(assert_all_called=False) as mock:
        yield mock.post(f"{MAIN}/chat/completions"), mock.post(f"{BACKUP}/chat/completions")


@pytest.mark.parametrize(
    "failure",
    [httpx.Response(503), httpx.Response(429, headers={"retry-after": "60"}), httpx.ConnectTimeout("timeout")],
    ids=["503", "429", "timeout"],
)
def test_backup_answers_when_main_fails(client, providers, failure, caplog):
    main, backup = providers
    main.mock(side_effect=failure) if isinstance(failure, Exception) else main.mock(return_value=failure)
    backup.mock(return_value=_completion())

    with caplog.at_level(logging.INFO, logger="app.providers.llm"):
        body = client.post("/api/v1/interpretations", json={"query": QUERY}).json()

    assert body["provider"] == "llm"
    assert body["fallback_reason"] is None
    sent = backup.calls.last.request
    assert sent.headers["authorization"] == "Bearer backup-key"
    assert json.loads(sent.content)["model"] == "some-model:free"
    assert "LLM answered with some-model:free (fallback)" in caplog.text


def test_main_ok_does_not_call_backup(client, providers):
    main, backup = providers
    main.mock(return_value=_completion())
    body = client.post("/api/v1/interpretations", json={"query": QUERY}).json()
    assert body["provider"] == "llm"
    assert not backup.called


def test_both_down_fall_back_to_rules(client, providers):
    main, backup = providers
    main.mock(return_value=httpx.Response(503))
    backup.mock(return_value=httpx.Response(500))
    body = client.post("/api/v1/interpretations", json={"query": QUERY}).json()
    assert body["provider"] == "mock"
    assert body["fallback_reason"] == "llm_unavailable"
    assert body["activity"]["normalized_category"] == "rubro_102"


def test_backup_alone_is_enough(client, override_settings):
    override_settings(llm_base_url="", llm_api_key="", llm_fallback_base_url=BACKUP, llm_fallback_api_key="backup-key")
    with respx.mock(assert_all_called=False) as mock:
        mock.post(f"{BACKUP}/chat/completions").mock(return_value=_completion())
        body = client.post("/api/v1/interpretations", json={"query": QUERY}).json()
    assert body["provider"] == "llm"
