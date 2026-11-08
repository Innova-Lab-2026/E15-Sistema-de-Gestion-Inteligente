"""Archivos que entrega el equipo de Data en `data/` (barrios, sinónimos, consultas de prueba).

Se leen una sola vez por proceso (`lru_cache`), igual que los snapshots de `app/db/`.
El formato de cada archivo lo controla `tests/test_data_files.py`.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

# Backend/data en el repo; /app/data en la imagen (Dockerfile: COPY data ./data).
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

BARRIOS_FILE = "barrios.csv"
SINONIMOS_FILE = "sinonimos.csv"
CONSULTAS_FILE = "consultas_prueba.csv"


@dataclass(frozen=True)
class Barrio:
    id: str
    nombre: str
    comuna: int
    variantes: tuple[str, ...]


def fold(text: str) -> str:
    """Forma de comparación: minúsculas, sin tildes ni puntuación, espacios simples.

    "VILLA GRAL. MITRE" -> "villa gral mitre", "Núñez" -> "nunez", "la_boca" -> "la boca".
    """
    decomposed = unicodedata.normalize("NFKD", text.lower())
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    cleaned = re.sub(r"[^a-z0-9ñ]+", " ", without_marks.replace("_", " "))
    return " ".join(cleaned.split())


def _read_csv(name: str) -> list[dict[str, str]]:
    path = DATA_DIR / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


@lru_cache
def barrios() -> tuple[Barrio, ...]:
    rows = _read_csv(BARRIOS_FILE)
    return tuple(
        Barrio(
            id=row["barrio_id"],
            nombre=row["nombre"],
            comuna=int(row["comuna"]),
            variantes=tuple(v.strip() for v in row.get("variantes", "").split("|") if v.strip()),
        )
        for row in rows
    )


@lru_cache
def _barrios_por_id() -> dict[str, Barrio]:
    return {b.id: b for b in barrios()}


@lru_cache
def variantes_de_barrios() -> dict[str, str]:
    """Forma plegada (`fold`) de cada nombre, id y variante -> barrio_id."""
    index: dict[str, str] = {}
    for barrio in barrios():
        for text in (barrio.id, barrio.nombre, *barrio.variantes):
            key = fold(text)
            if key:
                index.setdefault(key, barrio.id)
    return index


def barrio_por_variante(texto: str | None) -> str | None:
    """"NUÑEZ" -> "nunez", "Boca" -> "la_boca", "VILLA GRAL. MITRE" -> "villa_general_mitre"."""
    if not texto:
        return None
    return variantes_de_barrios().get(fold(texto))


def barrio(barrio_id: str | None) -> Barrio | None:
    return _barrios_por_id().get(barrio_id or "")


def comuna_de(barrio_id: str | None) -> int | None:
    found = barrio(barrio_id)
    return found.comuna if found else None


@lru_cache
def sinonimos() -> dict[str, str]:
    """Término ciudadano (tal como lo escribe Data) -> rubro_code."""
    return {row["termino"]: row["rubro_code"] for row in _read_csv(SINONIMOS_FILE) if row.get("termino")}


@lru_cache
def consultas_prueba() -> tuple[dict[str, str], ...]:
    return tuple(_read_csv(CONSULTAS_FILE))


@lru_cache
def meta(nombre_csv: str) -> dict[str, Any] | None:
    """Contenido de `<archivo>.meta.json` (fuente, licencia, fechas), o None si Data no lo entregó."""
    path = DATA_DIR / (Path(nombre_csv).stem + ".meta.json")
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
