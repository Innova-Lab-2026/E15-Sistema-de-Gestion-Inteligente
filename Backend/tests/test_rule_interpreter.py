"""B06: the rule interpreter matches whole words and removes the barrio and the address first."""

from __future__ import annotations

import pytest

from app.db.catalog_data import ACTIVITY_DEFINITIONS
from app.db.data_files import barrios
from app.providers.mock_interpreter import mock_interpret

CATALOG = {code: name for code, name, *_ in ACTIVITY_DEFINITIONS}


def _activity(query: str) -> str | None:
    return mock_interpret(query, CATALOG)["activity"]["normalized_category"]


BARRIO_TEXTS = sorted({text for b in barrios() for text in (b.nombre, *b.variantes) if "Ã" not in text})


@pytest.mark.parametrize("barrio", BARRIO_TEXTS)
def test_no_barrio_is_read_as_an_activity(barrio):
    assert _activity(f"quiero abrir un local en {barrio}") is None
    assert _activity(barrio) is None


@pytest.mark.parametrize(
    ("query", "code"),
    [
        ("quiero abrir una botica en Recoleta", "rubro_66"),  # "botica" ≠ "tic"
        ("quiero abrir una cafetería en Retiro", "rubro_102"),  # "Retiro" ≠ "tiro"
        ("quiero abrir una floreria en Flores", "rubro_171"),  # Flores es el barrio
        ("quiero abrir un gimnasio en Parque Chas", "rubro_242"),
        ("quiero abrir dos kioscos en Caballito", "rubro_245"),  # plural
        ("quiero abrir un maxikiosco en Flores", "rubro_169"),  # el más largo gana
        ("necesito abrir una farmacia en Caballito", "rubro_66"),
    ],
)
def test_activity_with_barrio(query, code):
    assert _activity(query) == code


@pytest.mark.parametrize(
    "query",
    [
        "qué clima hace hoy en Buenos Aires",
        "cómo saco el DNI",
        "cuánto sale un pasaje a Mar del Plata",
        "quiero abrir un negocio",
        "quiero abrir un local en Caballito",
    ],
)
def test_no_activity(query):
    assert _activity(query) is None


def test_street_named_like_a_barrio_is_the_address():
    result = mock_interpret("quiero abrir una farmacia en Av. Belgrano 1500", CATALOG)
    assert result["activity"]["normalized_category"] == "rubro_66"
    assert result["location"]["address"] == "Av. Belgrano 1500"


def test_raw_text_is_literal():
    result = mock_interpret("Quiero abrir una Cafetería en Av. Corrientes 2500", CATALOG)
    assert result["activity"]["raw_text"] == "Cafetería"
