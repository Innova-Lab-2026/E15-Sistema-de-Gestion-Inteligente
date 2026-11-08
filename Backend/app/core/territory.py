"""Territorial helpers shared by providers and services."""

from __future__ import annotations

import re

_COMMUNE_NUMBER = re.compile(r"\d{1,2}")


def normalize_commune(value: object) -> str | None:
    """Commune as a number from 1 to 15 in text: "Comuna 3", "COMUNA 03", 3 and "3" -> "3".

    USIG writes "Comuna 3" and the offices snapshot "3": comparing them raw drops the
    communal office. Anything that is not a commune of CABA returns None.
    """
    if value is None:
        return None
    match = _COMMUNE_NUMBER.search(str(value))
    if not match:
        return None
    number = int(match.group())
    return str(number) if 1 <= number <= 15 else None


def same_commune(a: object, b: object) -> bool:
    left = normalize_commune(a)
    return left is not None and left == normalize_commune(b)
