"""Texts for the person, one template per `reason` (B11).

The backend writes them with data it already validated (the words the person used, the barrio,
the address); never with text from the LLM and never with internal codes such as `rubro_102`.
The Frontend can show `message` or write its own text from `reason`.
"""

from __future__ import annotations

from app.schemas.interpretation import Reason

_MAX_QUOTED = 80


def _quote(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = " ".join(text.split())
    if len(cleaned) > _MAX_QUOTED:
        cleaned = cleaned[: _MAX_QUOTED - 1].rstrip() + "…"
    return cleaned or None


def message_for(
    reason: Reason | None,
    *,
    activity_text: str | None = None,
    has_candidates: bool = False,
    address: str | None = None,
    neighborhood: str | None = None,
    commune: str | None = None,
) -> str | None:
    activity_text = _quote(activity_text)
    address = _quote(address)
    if reason is None:
        return None
    if reason == "activity_missing":
        return "Contanos qué actividad querés hacer, por ejemplo «cafetería» o «ferretería»."
    if reason == "activity_not_in_catalog":
        what = f"«{activity_text}»" if activity_text else "esa actividad"
        if has_candidates:
            return f"No encontramos {what} en el catálogo. Elegí la actividad más parecida."
        return f"No encontramos {what} en el catálogo. Probá describirla con otras palabras, por ejemplo «kiosco» o «local de ropa»."
    if reason == "location_missing":
        return "Falta la dirección. Indicá calle y altura en la Ciudad de Buenos Aires, por ejemplo «Av. Corrientes 2500»."
    if reason == "location_neighborhood_only":
        where = f"el barrio {neighborhood}" if neighborhood else "el barrio"
        office = f"la sede de la Comuna {commune}" if commune else "la sede comunal"
        return (
            f"Con {where} te mostramos los trámites y {office}. "
            "Para revisar la zonificación indicá calle y altura."
        )
    if reason == "location_not_found":
        what = f"la dirección «{address}»" if address else "esa dirección"
        return f"No encontramos {what}. Revisá la calle y la altura."
    if reason == "location_ambiguous":
        what = f"La dirección «{address}»" if address else "La dirección"
        return f"{what} coincide con más de un lugar. Elegí el correcto."
    if reason == "location_outside_caba":
        return "La ubicación está fuera de la Ciudad de Buenos Aires. Por ahora solo orientamos trámites en CABA."
    if reason == "topic_out_of_scope":
        return (
            "Por ahora solo podemos orientarte para abrir o habilitar una actividad comercial "
            "en la Ciudad de Buenos Aires."
        )
    return None
