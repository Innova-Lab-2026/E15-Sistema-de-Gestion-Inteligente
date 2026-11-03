"""Smoke tests: every endpoint answers 200 with deterministic providers and the expected shape."""

from __future__ import annotations

import pytest

CORRIENTES = {"latitude": -34.604, "longitude": -58.413}
CAFETERIA_QUERY = "Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    ("path", "keys"),
    [
        ("/api/v1/activities", {"code", "name", "enabled"}),
        ("/api/v1/sources", {"id", "name", "url"}),
        ("/api/v1/offices", {"id", "name", "address", "latitude", "longitude"}),
    ],
)
def test_catalog_lists(client, path, keys):
    response = client.get(path)
    assert response.status_code == 200
    items = response.json()
    assert items, f"{path} returned an empty list: is the seed loaded?"
    assert keys <= items[0].keys()


def test_offices_filter(client):
    response = client.get("/api/v1/offices", params={"category": "rubro_102", "commune": "3"})
    assert response.status_code == 200
    offices = response.json()
    assert offices
    assert all("rubro_102" in office["activity_codes"] for office in offices)


def test_open_data(client):
    packages = client.get("/api/v1/open-data/packages")
    assert packages.status_code == 200
    assert packages.json()["packages"]

    context = client.get("/api/v1/open-data/gastronomy-context", params={"commune": "3"})
    assert context.status_code == 200
    assert context.json()["total_caba"] > 0


@pytest.mark.parametrize(
    ("address", "status"),
    [
        ("Av. Corrientes 2500", "confirmed"),
        ("Palermo", "ambiguous"),
        ("Mar del Plata", "out_of_scope"),
        ("Calle Inexistente 123", "not_found"),
    ],
)
def test_geocode(client, address, status):
    response = client.post("/api/v1/locations/geocode", json={"address": address})
    assert response.status_code == 200
    assert response.json()["status"] == status


def test_zoning(client):
    response = client.post("/api/v1/locations/zoning", json={**CORRIENTES, "activity_code": "rubro_102"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rubro_allowed"
    assert body["parcel"]["smp"]


def test_interpretation(client):
    response = client.post("/api/v1/interpretations", json={"query": CAFETERIA_QUERY})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready_for_geocoding"
    assert body["activity"]["normalized_category"] == "rubro_102"
    assert body["location"]["address"] == "Av. Corrientes 2500"


@pytest.mark.parametrize(
    "payload",
    [
        {"activity_code": "rubro_102", "address": "Av. Corrientes 2500"},
        {"query": CAFETERIA_QUERY},
    ],
    ids=["deterministic", "natural_language"],
)
def test_consultation_complete(client, payload):
    response = client.post("/api/v1/consultations", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "complete"
    assert body["location"]["status"] == "confirmed"
    assert body["zoning"] is not None
    assert body["steps"] and body["sources"]


def test_consultation_without_address_asks_for_it(client):
    response = client.post("/api/v1/consultations", json={"query": "Quiero abrir una cafeteria"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_clarification"
    assert body["data_status"]["missing"] == ["location"]
