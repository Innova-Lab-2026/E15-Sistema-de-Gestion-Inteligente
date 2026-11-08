"""B03: loader for the files Data delivers in data/."""

from __future__ import annotations

import pytest

from app.db import data_files


@pytest.mark.parametrize(
    ("texto", "barrio_id"),
    [
        ("NUÑEZ", "nunez"),
        ("Núñez", "nunez"),
        ("nunez", "nunez"),
        ("Boca", "la_boca"),
        ("La Boca", "la_boca"),
        ("VILLA GRAL. MITRE", "villa_general_mitre"),
        ("villa general mitre", "villa_general_mitre"),
        ("Montserrat", "monserrat"),
        ("  palermo ", "palermo"),
        ("Velez Sarsfield", "velez_sarsfield"),
    ],
)
def test_barrio_por_variante(texto, barrio_id):
    assert data_files.barrio_por_variante(texto) == barrio_id


@pytest.mark.parametrize("texto", ["", None, "Mar del Plata", "Corrientes 2500"])
def test_unknown_barrio(texto):
    assert data_files.barrio_por_variante(texto) is None


def test_comuna_de():
    assert data_files.comuna_de("balvanera") == 3
    assert data_files.comuna_de("belgrano") == 13
    assert data_files.comuna_de("no_existe") is None


def test_sinonimos():
    sinonimos = data_files.sinonimos()
    assert sinonimos["cafeteria"] == "rubro_102"
    assert sinonimos["botica"] == "rubro_66"
    assert all(code.startswith("rubro_") for code in sinonimos.values())


def test_meta_and_test_queries():
    assert data_files.meta("barrios.csv")["publicado"] == "2026-07-29"
    assert len(data_files.consultas_prueba()) >= 20
