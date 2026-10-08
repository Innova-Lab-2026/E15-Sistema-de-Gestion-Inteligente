"""Fetch oficinas oficiales CABA → app/db/offices_snapshot.json.

Fuentes:
- AGC / tramite habilitación (buenosaires.gob.ar)
- Sedes Comunales (BA Data CKAN)
Coordenadas WGS84 via USIG normalizar.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.tramites_curados import URL_HABILITACION
from app.providers.ba_data import DEFAULT_UA

OUT = ROOT / "app" / "db" / "offices_snapshot.json"
CSV_URL = (
    "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/"
    "ministerio-de-educacion/sedes-comunales/sedes_comunales.csv"
)
GEOJSON_URL = (
    "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/"
    "ministerio-de-educacion/sedes-comunales/sedes_comunales.geojson"
)
DATASET_URL = "https://data.buenosaires.gob.ar/dataset/sedes-comunales"
URL_AGC = (
    "https://buenosaires.gob.ar/gcaba_historico/justicia/"
    "agencia-gubernamental-de-control"
)
USIG_BASE = "https://servicios.usig.buenosaires.gob.ar/normalizar"


def _headers() -> dict[str, str]:
    return {"User-Agent": DEFAULT_UA}


def _geocode(addr: str) -> tuple[float | None, float | None, str | None]:
    variants: list[str] = []
    cleaned = addr.strip().strip('"')
    variants.append(cleaned)
    variants.append(re.sub(r",?\s*\d+\s*piso.*", "", cleaned, flags=re.I).strip())

    # "Apellido, Nombre 123" / "Calle, Título 123"
    m = re.match(r'^"?([^,"]+),\s*([^0-9"]+?)\s+(\d+)', cleaned)
    if m:
        surname, given, height = m.group(1).strip(), m.group(2).strip(), m.group(3)
        given_plain = re.sub(r"\b(Pres\.|Av\.)\b", "", given).strip(" ,")
        if "Av." in given or given.startswith("Av"):
            variants.append(f"{given_plain} Av. {height}")
        variants.append(f"{given_plain} {height}")
        variants.append(f"{surname} {height}")
        if "Av." in given:
            variants.append(f"Av. {given_plain} {height}")

    if "Barco Centenera" in cleaned:
        n = re.search(r"(\d+)", cleaned)
        if n:
            variants.append(f"Barco Centenera {n.group(1)}")
            variants.append(f"Av. del Barco Centenera {n.group(1)}")
    if "Humberto" in cleaned:
        variants.append("Humberto 1 250")
    if "Peron" in cleaned.replace("ó", "o").replace("Ó", "O") or "Perón" in cleaned:
        variants.append("Peron, Juan Domingo, Tte. General 2941")

    seen: set[str] = set()
    with httpx.Client(timeout=30, follow_redirects=True, headers=_headers()) as client:
        for variant in variants:
            variant = variant.strip().strip('"')
            if not variant or variant in seen:
                continue
            seen.add(variant)
            url = f"{USIG_BASE}/?direccion={quote(variant)}&geocodificar=true"
            try:
                response = client.get(url)
                response.raise_for_status()
                items = response.json().get("direccionesNormalizadas") or []
            except Exception as exc:  # noqa: BLE001
                print(f"  geocode error [{variant}]: {exc}")
                continue
            for item in items:
                coords = item.get("coordenadas") or {}
                lat = coords.get("y")
                lon = coords.get("x")
                if lat is None or lon is None:
                    continue
                return float(lat), float(lon), item.get("direccion") or variant
    return None, None, None


def _decode_csv(content: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = content.decode(enc)
        except UnicodeDecodeError:
            continue
        if "Comunal" in text or "Humberto" in text:
            return text
    return content.decode("utf-8", errors="replace")


def _sede_kind(gna: str, name: str) -> str:
    blob = f"{gna} {name}".lower()
    if "subsede" in blob:
        return "subsede"
    if "unidad" in blob:
        return "unidad_atencion"
    return "sede"


def build_snapshot() -> dict:
    lat_agc, lon_agc, norm_agc = _geocode("Tte. Gral. Juan Domingo Peron 2941")
    if lat_agc is None or lon_agc is None:
        raise RuntimeError("No se pudo geocodificar AGC Peron 2941")
    print(f"AGC -> {norm_agc} ({lat_agc}, {lon_agc})")

    agc = {
        "id": "office-001",
        "name": "Agencia Gubernamental de Control - Habilitaciones y Permisos",
        "organization": "GCBA / Agencia Gubernamental de Control",
        "type": "physical_office",
        "address": "Tte. Juan Domingo Perón 2941, CABA",
        "opening_hours": "Lunes a viernes de 9 a 13:30 h",
        "url": URL_HABILITACION,
        "latitude": lat_agc,
        "longitude": lon_agc,
        "commune": None,
        "neighborhood": "Balvanera",
        "status": "available",
        "phone": None,
        "normalized_address": norm_agc,
        "source_refs": ["tramite-habilitacion", "agc"],
    }
    online = {
        "id": "office-002",
        "name": "Habilitacion de actividad economica (SSIT / online)",
        "organization": "GCBA / Agencia Gubernamental de Control",
        "type": "online_channel",
        "address": "Online (miBA / SSIT)",
        "opening_hours": "Online",
        "url": URL_HABILITACION,
        "latitude": lat_agc,
        "longitude": lon_agc,
        "commune": None,
        "neighborhood": None,
        "status": "available",
        "phone": None,
        "normalized_address": None,
        "source_refs": ["tramite-habilitacion"],
    }

    response = httpx.get(CSV_URL, headers=_headers(), timeout=60, follow_redirects=True)
    response.raise_for_status()
    text = _decode_csv(response.content)
    reader = csv.DictReader(io.StringIO(text))
    sedes: list[dict] = []
    for index, row in enumerate(reader, start=1):
        name = (row.get("fna") or row.get("nombre") or f"Sede {index}").strip()
        addr = (row.get("dir") or row.get("domicilio") or "").strip()
        barrio = (row.get("bar") or row.get("barrio") or "").strip() or None
        com_raw = row.get("com") or row.get("comuna") or ""
        tel = (row.get("tel") or row.get("telefono") or "").strip() or None
        web = (row.get("web") or "").strip() or DATASET_URL
        gna = (row.get("gna") or "").strip()
        commune = str(int(com_raw)) if str(com_raw).isdigit() else (str(com_raw) or None)

        lat, lon, norm = _geocode(addr)
        print(f"{index:02d} {name}: {addr} -> {norm} ({lat}, {lon})")
        if lat is None or lon is None:
            raise RuntimeError(f"Geocode falló para sede: {name} / {addr}")

        sedes.append(
            {
                "id": f"office-sede-{index:02d}",
                "name": name,
                "organization": "GCBA / Gestion Comunal",
                "type": "physical_office",
                "address": f"{addr}, CABA",
                "opening_hours": None,
                "url": web,
                "latitude": lat,
                "longitude": lon,
                "commune": commune,
                "neighborhood": barrio,
                "status": "available",
                "phone": tel,
                "kind": _sede_kind(gna, name),
                "normalized_address": norm,
                "source_refs": ["ba-data-sedes-comunales"],
            }
        )

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "ba_data_sedes": {
                "dataset": DATASET_URL,
                "csv_url": CSV_URL,
                "geojson_url": GEOJSON_URL,
            },
            "habilitacion": {"url": URL_HABILITACION},
            "agc": {"url": URL_AGC},
        },
        "offices": [agc, online, *sedes],
    }


def main() -> None:
    snap = build_snapshot()
    OUT.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(snap['offices'])} offices)")


if __name__ == "__main__":
    main()
