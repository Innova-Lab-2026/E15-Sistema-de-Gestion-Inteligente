"""Reconoce un barrio de CABA en texto libre, sin LLM, con `data/barrios.csv`.

    "quiero poner una barbería en Belgrano"   -> belgrano (Comuna 13)
    "abrir cafeteria en velez sarsfield"      -> velez_sarsfield
    "en el barrio de Núñez" / "Gorriti 4500, Palermo" -> nunez / palermo

Para no confundir un barrio con otra cosa ("venta de flores", "Av. Belgrano 1500"), el barrio
cuenta solo si va después de "en", "barrio", "zona", "por" o una coma, o si está escrito con
mayúscula, y nunca dentro del tramo de la dirección.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from app.db.data_files import barrio, fold, variantes_de_barrios

_WORD = re.compile(r"[^\W_]+", re.UNICODE)
_INTRODUCERS = {"en", "barrio", "zona", "por"}
_INTRODUCERS_WITH_DE = {"barrio", "zona", "cerca"}


@dataclass(frozen=True)
class NeighborhoodMatch:
    barrio_id: str
    name: str  # nombre oficial, con tildes
    commune: int
    raw_text: str  # tal cual aparece en la consulta
    start: int
    end: int


@lru_cache
def _variants_by_words() -> list[tuple[tuple[str, ...], str]]:
    """Variantes partidas en palabras, las más largas primero ("villa general mitre" antes que "villa")."""
    items = [(tuple(key.split()), barrio_id) for key, barrio_id in variantes_de_barrios().items()]
    return sorted(items, key=lambda item: (-len(item[0]), -len(" ".join(item[0]))))


def _overlaps(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    return any(start < s_end and s_start < end for s_start, s_end in spans)


def _introduced(text: str, words: list[re.Match], index: int) -> bool:
    before = text[: words[index].start()].rstrip()
    if before.endswith(","):
        return True
    previous = [fold(w.group()) for w in words[max(0, index - 2) : index]]
    if previous and previous[-1] in _INTRODUCERS:
        return True
    # "en el barrio de X", "zona de X", "cerca de X".
    if len(previous) == 2 and previous[0] in _INTRODUCERS_WITH_DE and previous[1] in {"de", "del"}:
        return True
    return words[index].group()[:1].isupper()


def find_neighborhood(text: str, skip: list[tuple[int, int]] | None = None) -> NeighborhoodMatch | None:
    """Primer barrio mencionado en `text`, salteando los tramos de `skip` (por ejemplo la dirección)."""
    if not text:
        return None
    skip = skip or []
    words = list(_WORD.finditer(text))
    folded = [fold(w.group()) for w in words]
    for i in range(len(words)):
        for variant, barrio_id in _variants_by_words():
            n = len(variant)
            if tuple(folded[i : i + n]) != variant:
                continue
            start, end = words[i].start(), words[i + n - 1].end()
            if _overlaps(start, end, skip) or not _introduced(text, words, i):
                continue
            found = barrio(barrio_id)
            if found is None:
                continue
            return NeighborhoodMatch(
                barrio_id=found.id,
                name=found.nombre,
                commune=found.comuna,
                raw_text=text[start:end],
                start=start,
                end=end,
            )
    return None
