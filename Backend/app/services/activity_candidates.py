"""Candidates for the activity (B10): up to 3 enabled rubros, combining three sources.

1. Exact citizen synonym (`data/sinonimos.csv` + code aliases) -> score 1.0, match "synonym".
   A distinctive word of an official name counts here too, as match "name" (0.9 if only one
   rubro has it, 0.75 if two do).
2. The LLM: its `normalized_category` (score = its confidence) and its ordered
   `activity_candidates`, always filtered by the catalog -> match "llm".
3. Text similarity of the activity phrase with synonyms and official names (works without
   LLM) -> score = similarity, match "name".

Rule: the best one is taken as `normalized_category` only if its score is >= ACCEPT_SCORE and
it beats the second one by ACCEPT_MARGIN; otherwise the candidates go back with
`reason: activity_not_in_catalog`. The threshold is a pending decision with QA (ROADMAP).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from typing import Literal

from app.db.catalog_data import ACTIVITY_DEFINITIONS, activity_synonyms
from app.db.data_files import fold
from app.providers.mock_interpreter import find_activity, location_spans, name_token_index, without

ACCEPT_SCORE = 0.85
ACCEPT_MARGIN = 0.1
MAX_CANDIDATES = 3
# Below this similarity a rubro is not even suggested.
MIN_SIMILARITY = 0.7

Match = Literal["synonym", "llm", "name"]

# Words that are not the activity itself ("quiero abrir una ... en").
_PHRASE_STOPWORDS = {
    "quiero", "quisiera", "queria", "necesito", "me", "gustaria", "voy", "a", "al", "abrir", "poner",
    "montar", "habilitar", "habilito", "instalar", "emprender", "arrancar", "inaugurar", "tener",
    "como", "donde", "que", "cual", "un", "una", "unos", "unas", "el", "la", "los", "las", "lo",
    "en", "mi", "su", "nuevo", "nueva", "propio", "propia", "local", "negocio", "comercio",
    "emprendimiento", "algo", "para", "por", "con", "y", "o", "tengo", "hacer", "puedo", "hoy",
    "barrio", "zona", "calle", "avenida", "av", "cerca", "de", "del", "chico", "chica", "pequeno",
    "pequena", "grande",
}
_CONNECTORS = {"de", "del", "y", "para", "con"}
_WORD = re.compile(r"[^\W_]+", re.UNICODE)


@dataclass(frozen=True)
class Candidate:
    code: str
    name: str
    score: float
    match: Match


def activity_phrase(query: str) -> str | None:
    """The words that describe the activity, literal ("tienda de regalos"), without the address,
    the barrio and the "quiero abrir un ..." around them."""
    text = without(query, location_spans(query))
    words = list(_WORD.finditer(text))
    best: tuple[int, int] | None = None
    i = 0
    while i < len(words):
        if fold(words[i].group()) in _PHRASE_STOPWORDS:
            i += 1
            continue
        j = i
        # Join "tienda de regalos": a connector between two content words stays inside.
        while j + 1 < len(words) and text[words[j].end() : words[j + 1].start()].strip() == "" and (
            fold(words[j + 1].group()) not in _PHRASE_STOPWORDS
            or (
                fold(words[j + 1].group()) in _CONNECTORS
                and j + 2 < len(words)
                and fold(words[j + 2].group()) not in _PHRASE_STOPWORDS
            )
        ):
            j += 1
        if best is None or (words[j].end() - words[i].start()) > (best[1] - best[0]):
            best = (words[i].start(), words[j].end())
        i = j + 1
    if best is None:
        return None
    phrase = text[best[0] : best[1]].strip()
    return phrase if len(fold(phrase)) >= 4 else None


@lru_cache
def _official_names() -> list[tuple[str, str]]:
    """(rubro_code, nombre oficial plegado sin numeración ni paréntesis)."""
    out = []
    for code, name, *_ in ACTIVITY_DEFINITIONS:
        cleaned = re.sub(r"^[\d.\s]+", "", name)
        cleaned = re.sub(r"\([^)]*\)", " ", cleaned)
        out.append((code, fold(cleaned)))
    return out


def _ngrams(words: list[str], size: int) -> list[str]:
    return [" ".join(words[i : i + size]) for i in range(len(words) - size + 1)]


def _similarity(phrase: str, target: str) -> float:
    """Best ratio between the phrase and any piece of `target` of about the same length."""
    target_words = target.split()
    size = len(phrase.split())
    best = 0.0
    for n in {max(1, size - 1), size, size + 1}:
        for piece in _ngrams(target_words, n) or [target]:
            best = max(best, SequenceMatcher(None, phrase, piece).ratio())
    return best


def similar_candidates(phrase: str | None, catalog: dict[str, str]) -> list[Candidate]:
    if not phrase:
        return []
    folded = fold(phrase)
    scores: dict[str, float] = {}
    for term, code in activity_synonyms().items():
        if code in catalog:
            scores[code] = max(scores.get(code, 0.0), SequenceMatcher(None, folded, term).ratio())
    for code, name in _official_names():
        if code in catalog:
            scores[code] = max(scores.get(code, 0.0), _similarity(folded, name))
    return [
        Candidate(code, catalog[code], round(score, 3), "name")
        for code, score in scores.items()
        if score >= MIN_SIMILARITY
    ]


def rule_candidates(query: str, catalog: dict[str, str]) -> list[Candidate]:
    """Synonym or distinctive official word found in the query (no LLM)."""
    found = find_activity(without(query, location_spans(query)), catalog)
    if not found:
        return []
    code, term, kind = found
    if kind == "synonym":
        return [Candidate(code, catalog[code], 1.0, "synonym")]
    owners = [c for c in name_token_index().get(term, (code,)) if c in catalog]
    score = 0.9 if len(owners) == 1 else 0.75
    return [Candidate(c, catalog[c], score, "name") for c in owners]


def llm_candidates(raw_activity: dict, raw_candidates: object, catalog: dict[str, str]) -> list[Candidate]:
    """The LLM's choice and its ranked list, dropping codes outside the catalog."""
    out: list[Candidate] = []
    code = raw_activity.get("normalized_category")
    confidence = float(raw_activity.get("confidence") or 0.0)
    if isinstance(code, str) and code in catalog:
        out.append(Candidate(code, catalog[code], round(min(max(confidence, 0.0), 1.0), 3), "llm"))
    if isinstance(raw_candidates, list):
        top = out[0].score if out else 0.8
        for rank, item in enumerate(raw_candidates[:MAX_CANDIDATES]):
            other = item.get("code") if isinstance(item, dict) else item
            if isinstance(other, str) and other in catalog and other != code:
                out.append(Candidate(other, catalog[other], round(max(0.5, top - 0.1 * (rank + 1)), 3), "llm"))
    return out


def merge(candidates: list[Candidate]) -> list[Candidate]:
    """One per rubro (the highest score; on a tie synonym > llm > name), best first, at most 3."""
    priority = {"synonym": 0, "llm": 1, "name": 2}
    best: dict[str, Candidate] = {}
    for cand in candidates:
        current = best.get(cand.code)
        if current is None or (cand.score, -priority[cand.match]) > (current.score, -priority[current.match]):
            best[cand.code] = cand
    ranked = sorted(best.values(), key=lambda c: (-c.score, priority[c.match], c.code))
    return ranked[:MAX_CANDIDATES]


def pick(candidates: list[Candidate]) -> Candidate | None:
    """The first candidate if it is clear enough to continue without asking."""
    if not candidates or candidates[0].score < ACCEPT_SCORE:
        return None
    if len(candidates) > 1 and candidates[0].score - candidates[1].score < ACCEPT_MARGIN:
        return None
    return candidates[0]
