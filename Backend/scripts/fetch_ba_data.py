"""Fetch BA Data packages + ETL basico de oferta gastronomica → snapshot local."""

from __future__ import annotations

import csv
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.providers.ba_data import DEFAULT_UA, summarize_package

OUT = Path("app/db/ba_data_snapshot.json")
BASE = "https://data.buenosaires.gob.ar/api/3/action"
PACKAGE_IDS = [
    "oferta-establecimientos-gastronomicos",
    "comunas",
    "barrios",
    "api-consulta-datos-utiles",
    "codigo-urbanistico",
]


def _headers() -> dict[str, str]:
    return {"User-Agent": DEFAULT_UA}


def package_show(package_id: str) -> dict:
    r = httpx.get(
        f"{BASE}/package_show",
        params={"id": package_id},
        headers=_headers(),
        timeout=60,
        follow_redirects=True,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(f"package_show failed for {package_id}")
    return data["result"]


def _pick_resource(pkg: dict, *, fmt: str, name_contains: str | None = None) -> dict | None:
    fmt_u = fmt.upper()
    for res in pkg.get("resources") or []:
        if (res.get("format") or "").upper() != fmt_u:
            continue
        name = res.get("name") or ""
        if name_contains and name_contains.lower() not in name.lower():
            continue
        return res
    return None


def etl_gastronomia(pkg: dict) -> dict:
    csv_res = _pick_resource(pkg, fmt="CSV", name_contains="Oferta gastron")
    if csv_res is None:
        csv_res = _pick_resource(pkg, fmt="CSV")
    geo_res = None
    for res in pkg.get("resources") or []:
        fmt = (res.get("format") or "").upper()
        if "GEOJSON" in fmt or fmt == "JSON" and "geojson" in (res.get("url") or "").lower():
            geo_res = res
            break
        if "GeoJSON" in (res.get("name") or ""):
            geo_res = res
            break

    csv_url = (csv_res or {}).get("url")
    if not csv_url:
        return {"total": 0, "error": "csv_not_found"}

    raw = httpx.get(
        csv_url, headers=_headers(), timeout=120, follow_redirects=True
    )
    raw.raise_for_status()
    text = raw.content.decode("latin-1")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = list(reader)

    by_comuna = Counter((r.get("comuna") or "").strip() for r in rows if (r.get("comuna") or "").strip())
    by_barrio = Counter((r.get("barrio") or "").strip() for r in rows if (r.get("barrio") or "").strip())
    by_categoria = Counter(
        (r.get("categoria") or "").strip() for r in rows if (r.get("categoria") or "").strip()
    )

    # Muestra corta por comuna 3 / Balvanera (caso piloto)
    sample = []
    for r in rows:
        if (r.get("barrio") or "").strip().lower() == "balvanera":
            sample.append(
                {
                    "nombre": r.get("nombre"),
                    "categoria": r.get("categoria"),
                    "direccion": r.get("direccion_completa"),
                    "barrio": r.get("barrio"),
                    "comuna": r.get("comuna"),
                }
            )
        if len(sample) >= 8:
            break

    return {
        "total": len(rows),
        "csv_url": csv_url,
        "geojson_url": (geo_res or {}).get("url"),
        "by_comuna": dict(by_comuna.most_common()),
        "by_barrio": dict(by_barrio.most_common(40)),
        "by_categoria": dict(by_categoria.most_common()),
        "sample_balvanera": sample,
        "encoding": "latin-1",
        "delimiter": ";",
    }


def main() -> None:
    packages = []
    gastronomia = None
    for pid in PACKAGE_IDS:
        pkg = package_show(pid)
        packages.append(summarize_package(pkg))
        if pid == "oferta-establecimientos-gastronomicos":
            gastronomia = etl_gastronomia(pkg)
            print(f"gastronomia rows={gastronomia.get('total')}")

    payload = {
        "source": "https://data.buenosaires.gob.ar",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "package_ids": PACKAGE_IDS,
        "packages": packages,
        "gastronomia": gastronomia,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(packages)} packages)")


if __name__ == "__main__":
    main()
