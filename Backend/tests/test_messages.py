"""B11: every reason has a Spanish template; no message shows internal codes or LLM text."""

from __future__ import annotations

import re

import pytest

from app.schemas.interpretation import Reason
from app.services.messages import message_for
from tests.test_clarifications import CONSULTATION_CASES

CODE = re.compile(r"rubro_\w+|activity_|location_|_out_of_scope")


@pytest.mark.parametrize("reason", Reason.__args__)
def test_every_reason_has_a_template(reason):
    text = message_for(reason, activity_text="tienda de regalos", address="Florida 500", neighborhood="Belgrano", commune="13")
    assert text and text[0].isupper() and text.endswith(".")
    assert not CODE.search(text)


def test_templates_use_validated_data():
    assert message_for("activity_not_in_catalog", activity_text="tienda de regalos", has_candidates=True) == (
        "No encontramos «tienda de regalos» en el catálogo. Elegí la actividad más parecida."
    )
    assert "Comuna 13" in message_for("location_neighborhood_only", neighborhood="Belgrano", commune="13")
    assert "«Calle Falsa 123»" in message_for("location_not_found", address="Calle Falsa 123")
    assert message_for(None) is None
    long_text = "x" * 500
    assert len(message_for("activity_not_in_catalog", activity_text=long_text)) < 200


@pytest.mark.parametrize(("body", "status", "reason"), CONSULTATION_CASES, ids=[c[2] for c in CONSULTATION_CASES])
def test_consultation_message_matches_reason(client, body, status, reason):
    data = client.post("/api/v1/consultations", json=body).json()
    assert data["reason"] == reason
    assert data["message"], f"{reason} without message"
    assert not CODE.search(data["message"]) and not CODE.search(data["summary"])


@pytest.mark.parametrize(
    "query",
    [
        "quiero abrir un negocio",
        "quiero abrir algo en Av. Corrientes 2500",
        "quiero abrir una tienda de regalos en Florida 500",
        "quiero abrir una cafeteria",
        "cómo saco el DNI",
    ],
)
def test_interpretation_messages_have_no_codes(client, query):
    data = client.post("/api/v1/interpretations", json={"query": query}).json()
    assert data["message"]
    assert not CODE.search(data["message"])
