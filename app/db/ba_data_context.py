"""Contexto BA Data desde snapshot local (ETL basico)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

SNAPSHOT_PATH = Path(__file__).with_name("ba_data_snapshot.json")


@lru_cache
def load_ba_data_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_PATH.exists():
        return {"packages": [], "gastronomia": None}
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def _normalize_comuna(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip().lower()
    m = re.search(r"(\d{1,2})", text)
    if m:
        return str(int(m.group(1)))
    return text or None


def gastronomy_context(
    *,
    commune: str | None = None,
    neighborhood: str | None = None,
) -> dict[str, Any] | None:
    snap = load_ba_data_snapshot()
    gastro = snap.get("gastronomia")
    if not gastro:
        return None

    comuna_key = _normalize_comuna(commune)
    barrio_key = (neighborhood or "").strip()
    by_comuna = gastro.get("by_comuna") or {}
    by_barrio = gastro.get("by_barrio") or {}

    count_comuna = by_comuna.get(comuna_key) if comuna_key else None
    count_barrio = None
    if barrio_key:
        # match case-insensitive
        for name, n in by_barrio.items():
            if name.lower() == barrio_key.lower():
                count_barrio = n
                barrio_key = name
                break

    return {
        "dataset": "oferta-establecimientos-gastronomicos",
        "dataset_url": "https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos",
        "total_caba": gastro.get("total"),
        "comuna": comuna_key,
        "count_comuna": count_comuna,
        "barrio": barrio_key or None,
        "count_barrio": count_barrio,
        "by_categoria": gastro.get("by_categoria"),
        "csv_url": gastro.get("csv_url"),
        "geojson_url": gastro.get("geojson_url"),
        "fetched_at": snap.get("fetched_at"),
        "source_ids": ["source-002"],
    }


def map_layer_defs_from_snapshot() -> list[dict[str, Any]]:
    """Capas para seed a partir de recursos BA Data."""
    snap = load_ba_data_snapshot()
    layers: list[dict[str, Any]] = []
    for pkg in snap.get("packages") or []:
        pid = pkg.get("id")
        for res in pkg.get("resources") or []:
            fmt = (res.get("format") or "").upper()
            url = res.get("url")
            if not url:
                continue
            if fmt not in {"GEOJSON", "JSON", "CSV"} and "GEOJSON" not in (
                res.get("name") or ""
            ).upper():
                continue
            # Prefer geo layers for map
            if pid == "oferta-establecimientos-gastronomicos" and (
                "GEOJSON" in fmt or "geojson" in url.lower()
            ):
                layers.append(
                    {
                        "id": "layer-ba-gastro-geojson",
                        "name": "Oferta gastronomica (BA Data GeoJSON)",
                        "description": pkg.get("title"),
                        "layer_type": "geojson",
                        "url": url,
                        "status": "available",
                    }
                )
            if pid == "comunas" and (
                "GEOJSON" in fmt or "geojson" in url.lower() or fmt == "JSON"
            ):
                layers.append(
                    {
                        "id": "layer-ba-comunas",
                        "name": "Comunas CABA (BA Data)",
                        "description": pkg.get("title"),
                        "layer_type": "geojson",
                        "url": url,
                        "status": "available",
                    }
                )
            if pid == "barrios" and (
                "GEOJSON" in fmt or "geojson" in url.lower()
            ):
                layers.append(
                    {
                        "id": "layer-ba-barrios",
                        "name": "Barrios CABA (BA Data)",
                        "description": pkg.get("title"),
                        "layer_type": "geojson",
                        "url": url,
                        "status": "available",
                    }
                )
    # de-dupe by id
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for layer in layers:
        if layer["id"] in seen:
            continue
        seen.add(layer["id"])
        unique.append(layer)
    return unique
