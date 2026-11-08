"""B04: formato de los archivos que entrega Data en `data/`.

Si Data cambia un archivo y rompe el formato, este test falla diciendo qué archivo, qué fila
y qué arreglar. No necesita la base de datos ni la API.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import date

import pytest

from app.db.catalog_data import load_epok_rubros, rubro_code
from app.db.data_files import BARRIOS_FILE, CONSULTAS_FILE, DATA_DIR, SINONIMOS_FILE, fold

COLUMNS = {
    BARRIOS_FILE: ["barrio_id", "nombre", "comuna", "variantes"],
    SINONIMOS_FILE: ["termino", "rubro_code"],
}
# consultas_prueba.csv: estas columnas siempre; `estado_esperado` es opcional (B08).
CONSULTAS_COLUMNS = ["pregunta", "rubro_esperado", "barrio_esperado"]
CONSULTAS_OPTIONAL = ["estado_esperado"]
ESTADOS = {"completa", "pide_aclaracion", "fuera_de_alcance"}

META_KEYS = {"nombre", "url", "organismo", "licencia", "publicado", "descargado"}
# Pedidos a Data todavía sin entregar (ROADMAP, "Lo que esperamos de Data"). Cuando llegan, el
# test pasa solo (XPASS): sacar el archivo de esta lista para que vuelva a ser obligatorio.
META_PENDIENTES = {SINONIMOS_FILE, CONSULTAS_FILE}

BARRIO_ID = re.compile(r"^[a-z]+(_[a-z]+)*$")
RUBRO_CODES = {rubro_code(int(r["rubro_id"])) for r in load_epok_rubros()}


def _rows(name: str) -> tuple[list[str], list[dict[str, str]]]:
    raw = (DATA_DIR / name).read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), f"{name}: sacar el BOM (guardar como UTF-8 sin BOM)"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"{name}: no es UTF-8 (byte {exc.start}). Guardarlo como UTF-8.")
    reader = csv.DictReader(text.splitlines())
    rows = list(reader)
    return list(reader.fieldnames or []), rows


def _where(name: str, index: int) -> str:
    # +2: la fila 1 es el encabezado.
    return f"{name}, fila {index + 2}"


@pytest.mark.parametrize("name", list(COLUMNS))
def test_exact_columns(name):
    columns, rows = _rows(name)
    assert columns == COLUMNS[name], f"{name}: las columnas deben ser {COLUMNS[name]}, no {columns}"
    assert rows, f"{name}: no tiene filas"
    for i, row in enumerate(rows):
        empty = [c for c in COLUMNS[name] if c != "variantes" and not (row.get(c) or "").strip()]
        assert not empty, f"{_where(name, i)}: falta {', '.join(empty)}"


def test_barrios():
    _, rows = _rows(BARRIOS_FILE)
    seen: set[str] = set()
    for i, row in enumerate(rows):
        where = _where(BARRIOS_FILE, i)
        barrio_id = row["barrio_id"]
        assert BARRIO_ID.match(barrio_id), f"{where}: barrio_id {barrio_id!r} debe ir en minúsculas, sin tildes, con _"
        assert barrio_id not in seen, f"{where}: barrio_id {barrio_id!r} repetido"
        seen.add(barrio_id)
        assert row["comuna"].isdigit() and 1 <= int(row["comuna"]) <= 15, (
            f"{where}: comuna {row['comuna']!r} debe ser un número del 1 al 15"
        )
    assert len(seen) == 48, f"{BARRIOS_FILE}: CABA tiene 48 barrios y el archivo tiene {len(seen)}"


def test_no_variant_belongs_to_two_barrios():
    _, rows = _rows(BARRIOS_FILE)
    owners: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        texts = [row["barrio_id"], row["nombre"], *row["variantes"].split("|")]
        for text in filter(None, (t.strip() for t in texts)):
            owners[fold(text)].add(row["barrio_id"])
    clashes = {variant: sorted(ids) for variant, ids in owners.items() if len(ids) > 1}
    assert not clashes, f"{BARRIOS_FILE}: variantes que corresponden a más de un barrio: {clashes}"


def test_no_double_encoded_text():
    """`NÃºÃ±ez` (UTF-8 leído como Latin-1) está a propósito; `NuÃƒÂ±ez` es el error encodeado dos veces."""
    for name in (BARRIOS_FILE, SINONIMOS_FILE):
        for i, line in enumerate((DATA_DIR / name).read_text(encoding="utf-8").splitlines()):
            assert "Ãƒ" not in line and "Ã‚" not in line, (
                f"{name}, fila {i + 1}: texto convertido dos veces ({line!r}). Reescribir la variante."
            )


def test_synonyms():
    _, rows = _rows(SINONIMOS_FILE)
    seen: dict[str, int] = {}
    by_form: dict[str, set[str]] = defaultdict(set)
    for i, row in enumerate(rows):
        where = _where(SINONIMOS_FILE, i)
        term, code = row["termino"], row["rubro_code"]
        assert code in RUBRO_CODES, f"{where}: {code!r} no existe en epok_rubros_snapshot.json"
        key = term.strip().lower()
        assert key not in seen, f"{where}: {term!r} repetido (ya está en la fila {seen[key] + 2})"
        seen[key] = i
        by_form[fold(term)].add(code)
    # "cafeteria" y "cafetería" pueden estar los dos, pero con el mismo rubro.
    conflicts = {form: sorted(codes) for form, codes in by_form.items() if len(codes) > 1}
    assert not conflicts, f"{SINONIMOS_FILE}: el mismo término con y sin tilde va a rubros distintos: {conflicts}"


def test_test_queries():
    columns, rows = _rows(CONSULTAS_FILE)
    assert columns[: len(CONSULTAS_COLUMNS)] == CONSULTAS_COLUMNS and set(columns) <= {
        *CONSULTAS_COLUMNS,
        *CONSULTAS_OPTIONAL,
    }, f"{CONSULTAS_FILE}: columnas {columns}; deben ser {CONSULTAS_COLUMNS} (+ estado_esperado)"
    barrio_ids = {row["barrio_id"] for row in _rows(BARRIOS_FILE)[1]}
    preguntas: set[str] = set()
    for i, row in enumerate(rows):
        where = _where(CONSULTAS_FILE, i)
        assert row["pregunta"].strip(), f"{where}: falta la pregunta"
        assert row["pregunta"] not in preguntas, f"{where}: pregunta repetida"
        preguntas.add(row["pregunta"])
        rubro = row["rubro_esperado"].strip()
        assert not rubro or rubro in RUBRO_CODES, f"{where}: {rubro!r} no existe en epok"
        barrio = row["barrio_esperado"].strip()
        assert not barrio or barrio in barrio_ids, f"{where}: {barrio!r} no es un barrio_id de {BARRIOS_FILE}"
        estado = (row.get("estado_esperado") or "").strip()
        assert not estado or estado in ESTADOS, f"{where}: estado_esperado {estado!r} debe ser uno de {sorted(ESTADOS)}"


def test_only_known_files():
    """Un archivo con otro nombre (por ejemplo `consultas_prueba (1).csv`) no lo lee nadie."""
    known = {*COLUMNS, CONSULTAS_FILE}
    extra = sorted(p.name for p in DATA_DIR.glob("*.csv") if p.name not in known)
    assert not extra, f"data/: archivos que el backend no lee: {extra}. Renombrarlos o avisar a Backend."


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(n, marks=pytest.mark.xfail(reason=f"Data todavía no entregó {n[:-4]}.meta.json"))
        if n in META_PENDIENTES
        else n
        for n in (BARRIOS_FILE, SINONIMOS_FILE, CONSULTAS_FILE)
    ],
)
def test_each_csv_has_meta(name):
    path = DATA_DIR / (name[:-4] + ".meta.json")
    assert path.exists(), f"falta {path.name}"
    meta = json.loads(path.read_text(encoding="utf-8"))
    missing = META_KEYS - meta.keys()
    assert not missing, f"{path.name}: faltan {sorted(missing)}"
    for key in ("publicado", "descargado"):
        try:
            date.fromisoformat(meta[key])
        except ValueError:
            pytest.fail(f"{path.name}: {key} debe ser una fecha AAAA-MM-DD, no {meta[key]!r}")
