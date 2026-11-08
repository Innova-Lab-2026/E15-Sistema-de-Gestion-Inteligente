"""B13: data/*.meta.json becomes a source with its real date, URL, organization and license."""

from __future__ import annotations


def _sources(client) -> dict[str, dict]:
    return {s["id"]: s for s in client.get("/api/v1/sources").json()}


def test_barrios_source_has_real_dates(client):
    barrios = _sources(client)["source-data-barrios"]
    assert barrios["published_at"].startswith("2026-07-29")
    assert barrios["ingested_at"].startswith("2026-10-28")
    assert barrios["url"] == "https://data.buenosaires.gob.ar/dataset/barrios"
    assert barrios["organization"] == "GCBA / BA Data"
    assert barrios["license"] == "CC-BY-2.5-AR"


def test_only_files_with_meta_become_sources(client):
    ids = _sources(client)
    assert "source-data-sinonimos" not in ids, "sinonimos.meta.json is still pending from Data"


def test_neighborhood_consultation_cites_the_barrios_source(client):
    body = client.post("/api/v1/consultations", json={"activity_code": "rubro_315", "neighborhood_id": "belgrano"}).json()
    cited = {s["id"]: s for s in body["sources"]}
    assert "source-data-barrios" in cited
    assert cited["source-data-barrios"]["published_at"].startswith("2026-07-29")
    assert cited["source-data-barrios"]["license"] == "CC-BY-2.5-AR"
