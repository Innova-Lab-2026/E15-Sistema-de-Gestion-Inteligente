"""X-Interpreter: rules (only with DEBUG): test the local rules without spending LLM calls."""

from __future__ import annotations

import pytest
import respx

from tests.test_unrecognized import _export

LLM = "https://llm.test/v1"
QUERY = "Quiero abrir una cafeteria en Av. Corrientes 2500"
UNKNOWN = "quiero abrir una agencia de viajes en Florida 500"


@pytest.fixture
def llm(override_settings):
    def _configure(debug: bool):
        override_settings(llm_base_url=LLM, llm_api_key="test-key", debug=debug)

    with respx.mock(assert_all_called=False) as mock:
        route = mock.post(f"{LLM}/chat/completions")
        yield _configure, route


def test_rules_header_skips_the_llm_in_debug(client, llm):
    configure, route = llm
    configure(debug=True)

    body = client.post("/api/v1/interpretations", json={"query": QUERY}, headers={"X-Interpreter": "rules"}).json()

    assert body["provider"] == "mock"
    assert body["fallback_reason"] is None
    assert body["activity"]["normalized_category"] == "rubro_102"
    assert not route.called


def test_rules_header_is_ignored_without_debug(client, llm):
    configure, route = llm
    configure(debug=False)
    route.respond(500)

    body = client.post("/api/v1/interpretations", json={"query": QUERY}, headers={"X-Interpreter": "rules"}).json()

    # The LLM was called (and failed): the header did not change the provider.
    assert route.called
    assert body["fallback_reason"] == "llm_unavailable"


def test_status_says_if_the_header_is_available(client, override_settings):
    override_settings(debug=True)
    assert client.get("/status").json()["providers"]["llm"]["rules_header"] is True
    override_settings(debug=False)
    assert client.get("/status").json()["providers"]["llm"]["rules_header"] is False


def test_rules_only_queries_are_not_recorded_as_unrecognized(client, llm):
    configure, _ = llm
    configure(debug=True)

    body = client.post("/api/v1/interpretations", json={"query": UNKNOWN}, headers={"X-Interpreter": "rules"}).json()

    assert body["reason"] == "activity_not_in_catalog"
    assert body["activity"]["raw_text"] == "agencia de viajes"
    assert "agencia de viajes" not in {row["termino"] for row in _export()}
