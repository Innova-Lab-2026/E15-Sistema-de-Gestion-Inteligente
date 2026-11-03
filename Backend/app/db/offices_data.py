"""Oficinas oficiales desde snapshot (AGC + Sedes Comunales BA Data)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

SNAPSHOT_PATH = Path(__file__).with_name("offices_snapshot.json")


@lru_cache
def load_offices_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_PATH.exists():
        return {"offices": [], "sources": {}, "fetched_at": None}
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def office_defs_from_snapshot() -> list[dict[str, Any]]:
    snap = load_offices_snapshot()
    offices: list[dict[str, Any]] = []
    for raw in snap.get("offices") or []:
        oid = raw.get("id")
        if not oid:
            continue
        offices.append(
            {
                "id": oid,
                "name": raw["name"],
                "organization": raw.get("organization") or "GCBA",
                "type": raw.get("type") or "physical_office",
                "address": raw["address"],
                "opening_hours": raw.get("opening_hours"),
                "url": raw.get("url"),
                "latitude": float(raw["latitude"]),
                "longitude": float(raw["longitude"]),
                "commune": raw.get("commune"),
                "neighborhood": raw.get("neighborhood"),
                "status": raw.get("status") or "available",
            }
        )
    return offices
