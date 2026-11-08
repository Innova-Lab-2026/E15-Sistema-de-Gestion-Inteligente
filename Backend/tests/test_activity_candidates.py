"""B10: activity candidates (synonym, LLM, text similarity) and the rule to pick one."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from app.services.activity_candidates import Candidate, activity_phrase, merge, pick

LLM = "https://llm.test/v1"
REGALOS = "quiero abrir una tienda de regalos en Florida 500"


def _interpret(client, query: str) -> dict:
    return client.post("/api/v1/interpretations", json={"query": query}).json()


def test_tienda_de_regalos_suggests_rubro_16(client):
    data = _interpret(client, REGALOS)
    assert data["activity"]["normalized_category"] is None
    assert data["reason"] == "activity_not_in_catalog"
    assert data["activity"]["raw_text"] == "tienda de regalos"
    codes = [c["code"] for c in data["activity_candidates"]]
    assert "rubro_16" in codes
    assert 1 <= len(codes) <= 3
    assert all(c["match"] == "name" for c in data["activity_candidates"])
    scores = [c["score"] for c in data["activity_candidates"]]
    assert scores == sorted(scores, reverse=True)


def test_consultation_returns_candidates_and_completes_with_the_chosen_one(client):
    blocked = client.post("/api/v1/consultations", json={"query": REGALOS}).json()
    assert blocked["reason"] == "activity_not_in_catalog"
    assert "rubro_16" in [c["code"] for c in blocked["interpretation"]["activity_candidates"]]
    address = blocked["interpretation"]["location"]["address"]
    assert address == "Florida 500"

    # The person picks rubro_16: the frontend sends it back with the address.
    chosen = client.post("/api/v1/consultations", json={"activity_code": "rubro_16", "address": address}).json()
    assert chosen["status"] in {"complete", "partial"}
    assert chosen["reason"] is None
    assert chosen["interpretation"]["activity"]["normalized_category"] == "rubro_16"


def test_exact_synonym_is_taken_without_asking(client):
    data = _interpret(client, "quiero abrir una farmacia en Av. Corrientes 2500")
    assert data["activity"]["normalized_category"] == "rubro_66"
    assert data["activity_candidates"][0] == {"code": "rubro_66", "name": data["activity"]["display_name"], "score": 1.0, "match": "synonym"}


def test_typo_is_close_enough_to_continue(client):
    data = _interpret(client, "quiero abrir una farmasia en Av. Corrientes 2500")
    assert data["activity"]["normalized_category"] == "rubro_66"
    assert data["status"] == "ready_for_geocoding"


def test_typo_between_two_rubros_asks(client):
    # "Peluquería" is also the official name of rubro_206 (pets): too close to choose.
    data = _interpret(client, "quiero abrir una peluqeria en Av. Corrientes 2500")
    assert data["activity"]["normalized_category"] is None
    assert {"rubro_315", "rubro_206"} <= {c["code"] for c in data["activity_candidates"]}


@pytest.mark.parametrize(
    ("query", "phrase"),
    [
        (REGALOS, "tienda de regalos"),
        ("quiero abrir una joyería en Palermo", "joyería"),
        ("quiero abrir un negocio", None),
        ("quiero abrir algo en Av. Corrientes 2500", None),
    ],
)
def test_activity_phrase(query, phrase):
    assert activity_phrase(query) == phrase


def test_pick_rule():
    a = Candidate("rubro_1", "A", 0.95, "llm")
    b = Candidate("rubro_2", "B", 0.9, "name")
    assert pick([a]) == a
    assert pick([a, b]) is None, "no clear margin over the second"
    assert pick([Candidate("rubro_1", "A", 0.8, "name")]) is None, "below the threshold"
    assert merge([b, Candidate("rubro_2", "B", 1.0, "synonym")]) == [Candidate("rubro_2", "B", 1.0, "synonym")]


@pytest.fixture
def llm(override_settings):
    override_settings(llm_base_url=LLM, llm_api_key="test-key")
    with respx.mock(assert_all_called=False) as mock:
        yield mock.post(f"{LLM}/chat/completions")


def _llm(content: dict) -> httpx.Response:
    base = {
        "intent": "start_commercial_activity",
        "location": {"raw_text": "Florida 500", "address": "Florida 500", "confidence": 0.9},
        "jurisdiction": "CABA",
        "missing_fields": [],
        "status": "activity_unknown",
    }
    return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({**base, **content})}}]})


def test_llm_candidates_are_filtered_by_the_catalog(client, llm):
    llm.mock(
        return_value=_llm(
            {
                "activity": {"raw_text": "tienda de regalos", "normalized_category": None, "confidence": 0.3},
                "activity_candidates": ["rubro_16", "rubro_inventado", "rubro_245"],
            }
        )
    )
    data = _interpret(client, REGALOS)
    codes = [c["code"] for c in data["activity_candidates"]]
    assert "rubro_inventado" not in codes
    assert "rubro_16" in codes
    assert data["activity"]["normalized_category"] is None


def test_confident_llm_choice_is_taken(client, llm):
    llm.mock(
        return_value=_llm(
            {
                "activity": {"raw_text": "tienda de regalos", "normalized_category": "rubro_16", "confidence": 0.95},
                "activity_candidates": ["rubro_16"],
                "status": "ready_for_geocoding",
            }
        )
    )
    data = _interpret(client, REGALOS)
    assert data["activity"]["normalized_category"] == "rubro_16"
    assert data["activity_candidates"][0]["match"] == "llm"


def test_llm_down_still_gives_candidates(client, llm):
    llm.mock(return_value=httpx.Response(503))
    data = _interpret(client, REGALOS)
    assert data["provider"] == "mock"
    assert data["fallback_reason"] == "llm_unavailable"
    assert "rubro_16" in [c["code"] for c in data["activity_candidates"]]


def test_prompt_asks_for_candidates_and_no_question(client, llm):
    llm.mock(return_value=httpx.Response(500))
    _interpret(client, REGALOS)
    system = json.loads(llm.calls.last.request.content)["messages"][0]["content"]
    assert "activity_candidates" in system
    assert "clarification_question" not in system
