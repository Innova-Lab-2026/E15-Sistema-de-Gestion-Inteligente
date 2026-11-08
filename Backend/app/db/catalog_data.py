"""Catalogo de actividades = rubros oficiales Ciudad 3D / epok.

Fuente: GET /cur3d/cuadrosdeuso/rubros/?categoria=&mixtura=
Snapshot: app/db/epok_rubros_snapshot.json (regenerar con scripts/fetch_epok_rubros.py)

El `code` API es `rubro_{rubro_id}` para no inventar identificadores.
`name` es el texto oficial del rubro.
Los sinonimos ciudadanos solo ayudan a interpretar NL (mock/LLM), no reemplazan el catalogo.
La fuente de sinonimos es `data/sinonimos.csv` (equipo de Data); ver `activity_synonyms()`.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from app.db.data_files import fold, sinonimos

SNAPSHOT_PATH = Path(__file__).with_name("epok_rubros_snapshot.json")

EPOK_CATEGORIES: dict[int, str] = {
    1: "Comercial",
    2: "Depositos, Almacenamiento y logistica",
    3: "Servicios",
    4: "Alojamiento",
    5: "Transporte",
    6: "Diversiones publicas, cultura, culto y recreacion",
    7: "Educacion",
    8: "Sanidad",
    9: "Residencial",
    10: "Industria",
}

# Sinonimos del codigo (previos a data/sinonimos.csv) → rubro_id oficial (epok).
# Solo suman terminos que el CSV no define: nunca pisan un termino del CSV. Cubren, entre otros,
# los 17 rubros que el CSV no tiene, hasta que Data diga si los suma o se sacan (ROADMAP B05).
CITIZEN_ALIASES: dict[int, tuple[str, ...]] = {
    102: (
        "cafeteria",
        "cafetería",
        "cafe",
        "café",
        "restaurant",
        "restaurante",
        "parrilla",
        "pizzeria",
        "pizzería",
        "gastronomia",
        "gastronomía",
        "bar gastronomico",
        "bar gastronómico",
    ),
    471: (
        "confiteria",
        "confitería",
        "panaderia",
        "panadería",
        "pasteleria",
        "pastelería",
        "para llevar",
    ),
    309: ("ferreteria", "ferretería", "ferretero"),
    241: ("materiales de construccion", "materiales de construcción", "corralon", "corralón"),
    66: ("farmacia",),
    245: ("kiosco",),
    169: ("maxikiosco", "maxi kiosco"),
    137: ("supermercado", "minimercado"),
    16: ("local de ropa", "ropa", "indumentaria", "vestimenta", "tienda de ropa"),
    315: ("peluqueria", "peluquería", "barberia", "barbería", "salon de belleza", "salón de estética"),
    434: ("lavanderia", "lavandería", "tintoreria", "tintorería"),
    179: ("taller mecanico", "taller mecánico", "gomeria", "gomería", "mecanico", "mecánico"),
    41: ("estudio contable", "contable", "contador", "estudio profesional"),
    200: ("estudio juridico", "estudio jurídico", "abogado", "consultora"),
    242: ("gimnasio", "gym", "fitness"),
    285: ("servicio tecnico", "servicio técnico", "informatica", "informática", "tic"),
    91: ("hotel", "hospedaje"),
    51: ("hostel", "albergue"),
    45: ("alquiler temporario", "airbnb", "alojamiento temporario"),
    238: ("espacio cultural", "centro cultural"),
    5: ("academia", "instituto", "escuela", "colegio", "educacion", "educación"),
    104: ("veterinaria", "veterinario", "consultorio veterinario"),
    138: ("consultorio", "consultorio medico", "consultorio médico"),
    204: ("odontologo", "odontólogo", "dentista", "consultorio odontologico", "consultorio odontológico"),
    153: ("deposito", "depósito", "guardamuebles", "almacenaje"),
    136: ("pet shop", "petshop", "tienda de mascotas", "mascotas"),
    171: ("floreria", "florería", "flores", "vivero"),
    4: ("pintureria", "pinturería"),
}


# Terminos del CSV cuyo rubro Data todavia tiene que confirmar: se mantiene lo que hacia el codigo
# (None = no se usa como sinonimo). Sacar la linea cuando Data responda.
PENDING_SYNONYMS: dict[str, int | None] = {
    "veterinaria": 104,  # CSV: 136 (venta de animales); codigo: 104 (consultorio veterinario)
    "confiteria": 471,  # CSV: 102 (gastronomia); codigo: 471 (alimentacion para llevar)
    "comercio minorista": None,  # CSV: 16; ¿se saca? (demasiado generico)
}


def rubro_code(rubro_id: int) -> str:
    return f"rubro_{rubro_id}"


@lru_cache
def activity_synonyms() -> dict[str, str]:
    """Sinonimo ciudadano en forma plegada (`fold`) -> rubro_code.

    Orden: data/sinonimos.csv manda; los alias del codigo completan terminos que el CSV no
    tiene; los terminos pendientes de Data conservan el rubro que tenian en el codigo.
    """
    merged: dict[str, str] = {}
    for term, code in sinonimos().items():
        merged[fold(term)] = code
    for rubro_id, aliases in CITIZEN_ALIASES.items():
        for alias in aliases:
            merged.setdefault(fold(alias), rubro_code(rubro_id))
    for term, rubro_id in PENDING_SYNONYMS.items():
        if rubro_id is None:
            merged.pop(fold(term), None)
        else:
            merged[fold(term)] = rubro_code(rubro_id)
    return merged


def _tokens_from_official_name(name: str) -> tuple[str, ...]:
    cleaned = re.sub(r"^[\d.\s]+", "", name)
    cleaned = cleaned.replace("/", " ").replace("-", " ").replace(",", " ")
    cleaned = re.sub(r"\([^)]*\)", " ", cleaned)
    parts = [p.strip().lower() for p in re.split(r"\s+", cleaned) if len(p.strip()) >= 4]
    # quitar stopwords cortas frecuentes
    stop = {
        "local",
        "venta",
        "otros",
        "para",
        "como",
        "uso",
        "sin",
        "con",
        "general",
        "afines",
        "clase",
        "hasta",
        "estrellas",
        "gestion",
        "gestión",
        "privada",
        "estatal",
        "articulos",
        "artículos",
        "productos",
        "servicios",
        "actividad",
        "actividades",
        "empresa",
        "empresas",
    }
    return tuple(dict.fromkeys(p for p in parts if p not in stop))


@lru_cache
def load_epok_rubros() -> tuple[dict, ...]:
    raw = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return tuple(raw["rubros"])


def build_activity_definitions() -> list[tuple[str, str, str, int, int, tuple[str, ...]]]:
    """code, name, example, epok_category_id, epok_rubro_id, keywords.

    `keywords` son las palabras del nombre oficial: el interprete por reglas las usa solo
    despues de los sinonimos (`activity_synonyms`).
    """
    rows: list[tuple[str, str, str, int, int, tuple[str, ...]]] = []
    for item in load_epok_rubros():
        rid = int(item["rubro_id"])
        cat_id = int(item["categoria_id"])
        name = str(item["rubro"])
        code = rubro_code(rid)
        keywords = _tokens_from_official_name(name)
        if not keywords:
            keywords = (name.lower(),)
        example = f"Consulta orientativa: {name}"
        rows.append((code, name, example, cat_id, rid, keywords))
    return rows


# Tupla usada por seed / mock interpreter
ACTIVITY_DEFINITIONS: list[tuple[str, str, str, int, int, tuple[str, ...]]] = (
    build_activity_definitions()
)
