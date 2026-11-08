"""B08: Data's test queries (data/consultas_prueba.csv) with the rule interpreter (no LLM).

Every row is a test case, so each new case Data adds is picked up automatically. Compares the
activity (rubro_esperado), the barrio (barrio_esperado) and, when the column exists, the state
(estado_esperado: completa | pide_aclaracion | fuera_de_alcance).
"""

from __future__ import annotations

import pytest

from app.db.data_files import consultas_prueba

CASES = consultas_prueba()


def _state(consultation: dict) -> str:
    if consultation["status"] == "out_of_scope" or consultation.get("reason") in {
        "topic_out_of_scope",
        "location_outside_caba",
    }:
        return "fuera_de_alcance"
    if consultation["status"] in {"complete", "partial"}:
        return "completa"
    return "pide_aclaracion"


@pytest.mark.parametrize("case", CASES, ids=[c["pregunta"] for c in CASES])
def test_data_query(client, case):
    query = case["pregunta"]
    interpretation = client.post("/api/v1/interpretations", json={"query": query}).json()
    consultation = client.post("/api/v1/consultations", json={"query": query}).json()

    assert interpretation["provider"] == "mock"
    rubro = interpretation["activity"]["normalized_category"] or ""
    assert rubro == case["rubro_esperado"], f"rubro: {rubro or 'ninguno'} (esperado {case['rubro_esperado'] or 'ninguno'})"

    barrio = interpretation["location"].get("neighborhood_id") or consultation["location"].get("neighborhood_id") or ""
    assert barrio == case["barrio_esperado"], f"barrio: {barrio or 'ninguno'} (esperado {case['barrio_esperado'] or 'ninguno'})"

    expected_state = (case.get("estado_esperado") or "").strip()
    if expected_state:
        assert _state(consultation) == expected_state
