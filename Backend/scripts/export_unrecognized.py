"""Export the activities the system did not recognize, for Data to update data/sinonimos.csv (B16).

    python -m scripts.export_unrecognized                    # -> actividades_no_reconocidas.csv
    python -m scripts.export_unrecognized --output - --since 2026-11-01

One row per term (case and accents ignored): how many times it appeared, the rubro people
picked afterwards (if any) and the rubros the system suggested. Columns `termino` and
`rubro_code` are the same as in sinonimos.csv. The full queries are not exported.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.db.data_files import fold
from app.db.session import AsyncSessionLocal
from app.models import UnrecognizedActivity

COLUMNS = ["termino", "rubro_code", "veces", "veces_elegido", "candidatos", "primera_vez", "ultima_vez"]


async def build_rows(since: datetime | None = None) -> list[dict[str, object]]:
    async with AsyncSessionLocal() as session:
        query = select(UnrecognizedActivity).order_by(UnrecognizedActivity.created_at)
        if since is not None:
            query = query.where(UnrecognizedActivity.created_at >= since)
        records = list(await session.scalars(query))

    groups: dict[str, list[UnrecognizedActivity]] = defaultdict(list)
    for record in records:
        groups[fold(record.raw_text)].append(record)

    rows: list[dict[str, object]] = []
    for items in groups.values():
        chosen = Counter(r.chosen_code for r in items if r.chosen_code)
        suggested: Counter[str] = Counter()
        for r in items:
            for cand in r.candidates or []:
                if isinstance(cand, dict) and cand.get("code"):
                    suggested[cand["code"]] += 1
        rows.append(
            {
                "termino": Counter(r.raw_text.strip().lower() for r in items).most_common(1)[0][0],
                "rubro_code": chosen.most_common(1)[0][0] if chosen else "",
                "veces": len(items),
                "veces_elegido": chosen.most_common(1)[0][1] if chosen else 0,
                "candidatos": "|".join(code for code, _ in suggested.most_common(3)),
                "primera_vez": items[0].created_at.date().isoformat(),
                "ultima_vez": items[-1].created_at.date().isoformat(),
            }
        )
    return sorted(rows, key=lambda row: (-int(row["veces"]), str(row["termino"])))


def write_csv(rows: list[dict[str, object]], output: str) -> None:
    handle = sys.stdout if output == "-" else Path(output).open("w", encoding="utf-8", newline="")
    try:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if handle is not sys.stdout:
            handle.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", default="actividades_no_reconocidas.csv", help="archivo, o - para la pantalla")
    parser.add_argument("--since", help="solo desde esta fecha (AAAA-MM-DD)")
    args = parser.parse_args(argv)
    since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc) if args.since else None
    rows = asyncio.run(build_rows(since))
    write_csv(rows, args.output)
    if args.output != "-":
        print(f"{len(rows)} términos -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
