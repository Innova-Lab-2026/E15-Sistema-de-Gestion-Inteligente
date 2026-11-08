"""B05: data/sinonimos.csv is the source of citizen synonyms."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from app.db.catalog_data import ACTIVITY_DEFINITIONS, PENDING_SYNONYMS, activity_synonyms, rubro_code
from app.db.data_files import fold, sinonimos
from app.providers.mock_interpreter import mock_interpret

CATALOG = {code: name for code, name, *_ in ACTIVITY_DEFINITIONS}
PENDING = {fold(term): (rubro_code(rid) if rid else None) for term, rid in PENDING_SYNONYMS.items()}


@pytest.mark.parametrize(("term", "code"), sorted(sinonimos().items()))
def test_every_csv_term_gives_its_rubro(term, code):
    expected = PENDING.get(fold(term), code)
    result = mock_interpret(f"quiero abrir {term}", CATALOG)["activity"]["normalized_category"]
    if fold(term) in PENDING and expected is None:
        assert result != code, f"{term!r} is pending with Data and must not be used as a synonym"
    else:
        assert result == expected, f"{term!r} should give {expected}"


def test_csv_wins_over_code_aliases():
    synonyms = activity_synonyms()
    # In the code "ropa" and "restaurant" stay (the CSV does not define them), but never against the CSV.
    for term, code in sinonimos().items():
        if fold(term) not in PENDING:
            assert synonyms[fold(term)] == code
    assert synonyms["ropa"] == "rubro_16"
    assert synonyms["gimnasio"] == "rubro_242", "rubros only in the code are kept until Data answers"


def test_llm_prompt_includes_synonyms(client, override_settings):
    override_settings(llm_base_url="https://llm.test/v1", llm_api_key="test-key")
    with respx.mock(assert_all_called=False) as mock:
        route = mock.post("https://llm.test/v1/chat/completions").mock(return_value=httpx.Response(500))
        client.post("/api/v1/interpretations", json={"query": "quiero abrir una botica en Corrientes 2500"})
    prompt = json.loads(route.calls.last.request.content)["messages"][1]["content"]
    assert '"botica": "rubro_66"' in prompt
