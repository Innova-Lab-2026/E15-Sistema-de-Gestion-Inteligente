"""Fetch official rubros from epok and write JSON snapshot."""

from __future__ import annotations

import json
from pathlib import Path

import httpx

BASE = "https://epok.buenosaires.gob.ar"
OUT = Path("app/db/epok_rubros_snapshot.json")


def main() -> None:
    cats = httpx.get(f"{BASE}/cur3d/categorias/", timeout=60).json()
    all_rubros: dict[int, dict] = {}
    for c in cats:
        cid = c["id"]
        cname = c["nombre"]
        for m in (1, 2, 3, 4):
            r = httpx.get(
                f"{BASE}/cur3d/cuadrosdeuso/rubros/",
                params={"categoria": cid, "mixtura": m},
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            for item in data.get("rubros", []):
                rid = int(item["rubro_id"])
                if rid not in all_rubros:
                    all_rubros[rid] = {
                        "rubro_id": rid,
                        "rubro": item["rubro"],
                        "categoria_id": cid,
                        "categoria": data.get("categoria") or cname,
                        "mixturas": [m],
                    }
                elif m not in all_rubros[rid]["mixturas"]:
                    all_rubros[rid]["mixturas"].append(m)

    rows = sorted(all_rubros.values(), key=lambda x: (x["categoria_id"], x["rubro_id"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"source": f"{BASE}/cur3d/cuadrosdeuso/rubros/", "count": len(rows), "rubros": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(rows)} rubros -> {OUT}")


if __name__ == "__main__":
    main()
