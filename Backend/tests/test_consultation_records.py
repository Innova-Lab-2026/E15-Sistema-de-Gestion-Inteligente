"""B20: every consultation is stored and can be read again by consultation_id."""

from __future__ import annotations

import json

import httpx
import psycopg2
import respx

from tests.conftest import TEST_DATABASE_URL

QUERY = "Quiero abrir una cafeteria en Av. Corrientes 2500"


def _row(consultation_id: str) -> dict:
    from urllib.parse import urlparse

    url = urlparse(TEST_DATABASE_URL.replace("+asyncpg", ""))
    conn = psycopg2.connect(
        host=url.hostname, port=url.port or 5432, user=url.username, password=url.password, dbname=url.path.lstrip("/")
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT query, status, reason, provider, llm_model, prompt_version, source_ids, interpretation, location"
                " FROM consultations WHERE id = %s",
                (consultation_id,),
            )
            names = [d[0] for d in cur.description]
            values = cur.fetchone()
    finally:
        conn.close()
    assert values is not None, f"{consultation_id} was not stored"
    return dict(zip(names, values, strict=True))


def test_every_consultation_id_can_be_read_back(client):
    created = client.post("/api/v1/consultations", json={"query": QUERY}).json()
    again = client.get(f"/api/v1/consultations/{created['consultation_id']}")
    assert again.status_code == 200
    assert again.json() == created


def test_blocked_consultations_are_stored_too(client):
    created = client.post("/api/v1/consultations", json={"query": "quiero abrir un negocio"}).json()
    row = _row(created["consultation_id"])
    assert row["status"] == "needs_clarification"
    assert row["reason"] == "activity_missing"
    assert client.get(f"/api/v1/consultations/{created['consultation_id']}").json()["reason"] == "activity_missing"


def test_record_has_query_interpretation_location_sources_and_provider(client):
    created = client.post("/api/v1/consultations", json={"query": QUERY}).json()
    row = _row(created["consultation_id"])
    assert row["query"] == QUERY
    assert row["provider"] == "mock"
    assert row["llm_model"] is None
    assert row["prompt_version"] == "interpret-v2"
    assert row["interpretation"]["activity"]["normalized_category"] == "rubro_102"
    assert row["location"]["neighborhood_id"] == "balvanera"
    assert set(row["source_ids"]) == {s["id"] for s in created["sources"]}


def test_record_keeps_the_model_that_answered(client, override_settings):
    override_settings(llm_base_url="https://llm.test/v1", llm_api_key="k", llm_model="gemini-flash-lite-latest")
    content = {
        "intent": "start_commercial_activity",
        "activity": {"raw_text": "cafeteria", "normalized_category": "rubro_102", "confidence": 0.9},
        "location": {"raw_text": "Av. Corrientes 2500", "address": "Av. Corrientes 2500", "confidence": 0.9},
        "jurisdiction": "CABA",
        "missing_fields": [],
        "status": "ready_for_geocoding",
    }
    with respx.mock(assert_all_called=False) as mock:
        mock.post("https://llm.test/v1/chat/completions").mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(content)}}]})
        )
        created = client.post("/api/v1/consultations", json={"query": QUERY}).json()
    row = _row(created["consultation_id"])
    assert (row["provider"], row["llm_model"]) == ("llm", "gemini-flash-lite-latest")


def test_deterministic_consultation_has_no_provider(client):
    created = client.post("/api/v1/consultations", json={"activity_code": "rubro_102", "address": "Av. Corrientes 2500"}).json()
    row = _row(created["consultation_id"])
    assert row["query"] is None and row["provider"] is None and row["prompt_version"] is None


def test_unknown_consultation_is_404(client):
    response = client.get("/api/v1/consultations/consultation-doesnotexist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
