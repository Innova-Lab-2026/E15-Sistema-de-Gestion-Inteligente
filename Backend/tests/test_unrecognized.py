"""B16: activities not in the catalog are logged with the rubro chosen afterwards, and exported for Data."""

from __future__ import annotations

import csv
import io
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUERY = "quiero abrir una tienda de regalos en Florida 500"


def _export() -> list[dict[str, str]]:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.export_unrecognized", "--output", "-"],
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=True,
    )
    return list(csv.DictReader(io.StringIO(result.stdout)))


def test_unrecognized_activity_is_logged_and_exported_with_the_choice(client):
    client.post("/api/v1/interpretations", json={"query": QUERY, "conversation_id": "conv-b16"})
    # The person picks rubro_16 among the candidates, in the same conversation.
    client.post(
        "/api/v1/consultations",
        json={"activity_code": "rubro_16", "address": "Florida 500", "conversation_id": "conv-b16"},
    )
    # A second person, without choosing.
    client.post("/api/v1/consultations", json={"query": "Quiero abrir una Tienda de Regalos en Florida 500"})

    rows = {row["termino"]: row for row in _export()}
    row = rows["tienda de regalos"]
    assert int(row["veces"]) >= 2
    assert row["rubro_code"] == "rubro_16"
    assert int(row["veces_elegido"]) >= 1
    assert "rubro_16" in row["candidatos"].split("|")
    assert list(row) == ["termino", "rubro_code", "veces", "veces_elegido", "candidatos", "primera_vez", "ultima_vez"]


def test_recognized_activities_are_not_logged(client):
    client.post("/api/v1/interpretations", json={"query": "quiero abrir una farmacia en Av. Corrientes 2500"})
    assert "farmacia" not in {row["termino"] for row in _export()}
