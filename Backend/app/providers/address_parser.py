"""Reconocedor de direcciones de CABA en texto libre, sin LLM.

Lo usa el intérprete por reglas (`mock_interpreter`) cuando el LLM no está disponible, y
`InterpretationService` para pasar a cifras la altura que el LLM devuelva escrita en palabras.

Entiende alturas escritas de muchas formas y las devuelve en cifras:

    "Monroe al mil"                 -> "Monroe 1000"
    "Monroe mil quinientos"         -> "Monroe 1500"
    "Monroe milquinientos"          -> "Monroe 1500"   (palabras pegadas)
    "Monroe mil-quinientos"         -> "Monroe 1500"
    "Monroe mil kinientos"          -> "Monroe 1500"   (errores de ortografía: k/qu, c/s/z, v/b)
    "calle Olazábal ocho dos uno"   -> "calle Olazábal 821"   (cifra por cifra)
    "Rivadavia quince cuarenta"     -> "Rivadavia 1540"       (de a dos cifras)
    "Av. Corrientes 2.500"          -> "Av. Corrientes 2500"
    "Monroe al 2 mil"               -> "Monroe 2000"   (cifra + "mil"; también "2 mil 500")
    "Monroe 2000 o 2500"            -> "Monroe 2000"   (aproximada: se usa la primera altura)

El nombre de la calle se copia tal cual: "Tres Arroyos 500" o "9 de Julio 1000" no se tocan.
No corrige ni completa calles: eso lo hace USIG después.

Si no hay altura, reconoce esquinas, que USIG acepta como cruce de calles:

    "Corrientes y Callao" / "Corrientes esquina Callao" / "Corrientes esq. Callao"
                                    -> "Corrientes y Callao"
    "Corrientes entre Callao y Riobamba"
                                    -> "Corrientes y Callao"  (primera esquina, aproximada)

"y" también separa ideas ("en Corrientes y tengo dos empleados"): es esquina solo si las dos
partes parecen nombres de calle (con mayúscula y sin palabras como "tengo" o "local").
Las calles en minúscula y sin "en" ("una cafeteria monroe 1500") necesitan el callejero
oficial de USIG y todavía no se reconocen (ROADMAP B27).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

from app.db.data_files import barrio_por_variante

# ---------------------------------------------------------------------------
# Números en palabras
# ---------------------------------------------------------------------------

_UNITS = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9}
_TEENS = {
    "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiuno": 21, "veintidos": 22, "veintitres": 23, "veinticuatro": 24,
    "veinticinco": 25, "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
}
_TENS = {"treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90}
_HUNDREDS = {
    "cien": 100, "ciento": 100, "doscientos": 200, "trescientos": 300, "cuatrocientos": 400,
    "quinientos": 500, "seiscientos": 600, "setecientos": 700, "ochocientos": 800, "novecientos": 900,
}

# Calles y avenidas de CABA llegan hasta ~16.000; 5 cifras deja margen.
_MAX_NUMBER = 99_999


def _fold(text: str) -> str:
    """Minúsculas y sin tildes."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn").lower()


def _phonetic(word: str) -> str:
    """Clave que iguala errores de ortografía comunes: qu/k, c/s/z, v/b, h muda, letras dobles."""
    w = _fold(word)
    w = w.replace("qu", "k").replace("ce", "se").replace("ci", "si")
    w = w.replace("z", "s").replace("c", "k").replace("v", "b").replace("h", "")
    return re.sub(r"(.)\1+", r"\1", w)


def _build_lexicon() -> dict[str, tuple[str, int]]:
    lexicon: dict[str, tuple[str, int]] = {"cero": ("zero", 0), "mil": ("mil", 1000)}
    for kind, words in (("unit", _UNITS), ("teen", _TEENS), ("tens", _TENS), ("hund", _HUNDREDS)):
        for word, value in words.items():
            lexicon[word] = (kind, value)
    return {_phonetic(word): entry for word, entry in lexicon.items()}


_LEXICON = _build_lexicon()
# Con 6 letras habría falsos positivos ("viento" ~ "ciento", "cuadro" ~ "cuatro").
_FUZZY_MIN_LENGTH = 7
_FUZZY_KEYS = [key for key in _LEXICON if len(key) >= _FUZZY_MIN_LENGTH]


def _levenshtein_le1(a: str, b: str) -> bool:
    """True si a y b difieren en a lo sumo una letra (cambio, falta o sobra)."""
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = j = edits = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        edits += 1
        if edits > 1:
            return False
        if len(a) == len(b):
            i += 1
        j += 1
    return edits + (len(b) - j) <= 1


def _segment(key: str) -> list[tuple[str, int]] | None:
    """Parte palabras pegadas ("milkinientos" -> mil + quinientos). Necesita al menos dos partes."""
    n = len(key)
    best: list[list[tuple[str, int]] | None] = [None] * (n + 1)
    best[0] = []
    for end in range(2, n + 1):
        for start in range(end - 2, -1, -1):
            prefix = best[start]
            piece = _LEXICON.get(key[start:end])
            if prefix is not None and piece is not None:
                candidate = [*prefix, piece]
                if best[end] is None or len(candidate) < len(best[end]):
                    best[end] = candidate
    parts = best[n]
    return parts if parts and len(parts) >= 2 else None


@lru_cache(maxsize=2048)
def _number_word(word: str) -> tuple[tuple[str, int], ...] | None:
    """Una palabra -> sus valores numéricos, o None si no es un número."""
    key = _phonetic(word)
    if not key or not key.isalpha():
        return None
    if key in _LEXICON:
        return (_LEXICON[key],)
    parts = _segment(key)
    if parts:
        return tuple(parts)
    if len(key) >= _FUZZY_MIN_LENGTH:
        matches = [k for k in _FUZZY_KEYS if _levenshtein_le1(key, k)]
        if len(matches) == 1:
            return (_LEXICON[matches[0]],)
    return None


# Qué puede venir después de cada parte dentro de un mismo número.
_FOLLOWS = {
    "mil": {"start", "unit", "teen", "tens", "hund"},
    "hund": {"start", "mil"},
    "tens": {"start", "mil", "hund"},
    "teen": {"start", "mil", "hund"},
    "unit": {"start", "mil", "hund", "tens", "y"},
    "y": {"tens"},
}


def words_to_number(entries: list[tuple[str, int]]) -> int | None:
    """Convierte las partes de un número a entero.

    Si las partes no forman un solo número ("ocho dos uno", "quince cuarenta"), se leen como
    grupos que se escriben uno al lado del otro: 8|2|1 -> 821, 15|40 -> 1540.
    """
    chunks: list[int] = []
    total = part = 0
    last = "start"
    has_mil = False

    def close() -> bool:
        nonlocal total, part, last, has_mil
        if last == "start":
            return True
        if last == "y":
            return False
        chunks.append(total + part)
        total = part = 0
        last = "start"
        has_mil = False
        return True

    for kind, value in entries:
        if kind == "zero":
            if not close():
                return None
            chunks.append(0)
            continue
        fits = last in _FOLLOWS[kind] and not (kind == "mil" and has_mil)
        if not fits:
            if not close():
                return None
        if kind == "mil":
            total = (part or 1) * 1000
            part = 0
            has_mil = True
        elif kind != "y":
            part += value
        last = kind
    if not close() or not chunks:
        return None

    digits = "".join(str(c) for c in chunks) if len(chunks) > 1 else str(chunks[0])
    number = int(digits)
    if not 1 <= number <= _MAX_NUMBER:
        return None
    return number


# ---------------------------------------------------------------------------
# Direcciones
# ---------------------------------------------------------------------------

_TOKEN = re.compile(
    r"(?P<num>\d{1,3}(?:\.\d{3})+(?!\d)|\d+)"
    r"|(?P<sign>[nN]\s?[°º])"
    r"|(?P<word>[^\W\d_]+(?:\.)?)"
    r"|(?P<punct>[.,;:?!¿¡()\"])",
    re.UNICODE,
)

# Abreviaturas que terminan en punto sin cortar la oración.
_ABBREVIATIONS = {
    "av", "avda", "pje", "diag", "bv", "bvd", "nro", "num", "gral", "dr", "pte", "cnel",
    "tte", "sta", "sto", "ing", "pres", "int", "cap", "alte", "mcal", "hno", "pasj", "esq",
}
# Palabras que marcan dónde empieza el nombre de la calle (no forman parte de él).
_PREPOSITIONS = {"en", "sobre", "por"}
# Tipos de calle: forman parte del nombre y marcan su comienzo.
_STREET_TYPES = {
    "calle", "av", "avenida", "avda", "pasaje", "pje", "pasj", "diagonal", "diag",
    "boulevard", "bulevar", "bv", "bvd", "autopista", "camino",
}
# Entre el nombre de la calle y la altura.
_BEFORE_NUMBER = {"al", "altura", "nro", "numero", "num", "n"}
# Conectores que pueden ir dentro del nombre de una calle.
_CONNECTORS = {"de", "del", "la", "las", "el", "los", "y"}
# Si aparecen en el "nombre de la calle", no es una dirección.
_NOT_STREET = {
    "quiero", "quisiera", "queria", "abrir", "poner", "montar", "habilitar", "tengo", "tiene",
    "local", "negocio", "comercio", "un", "una", "unos", "unas", "mi", "con", "para", "que",
    "o", "porque", "donde", "como", "es", "esta", "hay", "cerca", "entre", "frente", "a",
    "ubicado", "ubicada", "queda", "hoy", "mañana", "manana", "barrio", "zona",
}
# Si vienen después del número, el número no es una altura ("50 metros", "2 empleados").
_NOT_HEIGHT_AFTER = {
    "metro", "metros", "mts", "mt", "m", "m2", "cuadra", "cuadras", "empleado", "empleados",
    "persona", "personas", "ano", "anos", "año", "años", "mes", "meses", "peso", "pesos",
    "dolar", "dolares", "mesa", "mesas", "silla", "sillas", "local", "locales", "hora", "horas",
    "hs", "por", "piso", "pisos", "km", "kilometros", "minutos", "dias",
}


@dataclass(frozen=True)
class _Token:
    text: str  # tal cual aparece, sin el punto final si no es abreviatura
    start: int
    end: int
    kind: str  # num | sign | word | punct
    ends_sentence: bool = False  # palabra seguida de un punto que no es de abreviatura

    @property
    def folded(self) -> str:
        return _fold(self.text).rstrip(".")


@dataclass(frozen=True)
class ParsedAddress:
    raw_text: str  # tramo literal de la consulta ("Monroe al mil quinientos")
    address: str  # calle + altura en cifras ("Monroe 1500"), lista para USIG
    street: str
    number: int  # 0 en una esquina
    start: int = 0  # posición del tramo en el texto original
    end: int = 0
    cross_street: str | None = None  # la otra calle de la esquina
    approximate: bool = False  # "entre calles" (primera esquina) o "2000 o 2500" (primera altura)


def _tokenize(text: str) -> list[_Token]:
    tokens: list[_Token] = []
    for match in _TOKEN.finditer(text):
        kind = match.lastgroup or "punct"
        value = match.group()
        if kind == "word" and value.endswith(".") and _fold(value[:-1]) not in _ABBREVIATIONS:
            tokens.append(_Token(value[:-1], match.start(), match.end() - 1, "word", ends_sentence=True))
            continue
        tokens.append(_Token(value, match.start(), match.end(), kind))
    return tokens


def _mil_remainder(tokens: list[_Token], start: int) -> tuple[int, int] | None:
    """Lo que sigue a "2 mil": una cifra ("500") o palabras ("quinientos"), menor que 1000."""
    if tokens[start - 1].ends_sentence or start >= len(tokens):
        return None
    tok = tokens[start]
    if tok.kind == "num":
        value = int(tok.text.replace(".", ""))
        return (value, start + 1) if 1 <= value < 1000 else None
    entries: list[tuple[str, int]] = []
    j = start
    while j < len(tokens) and tokens[j].kind == "word":
        parts = _number_word(tokens[j].text)
        if parts is None or any(kind == "mil" for kind, _ in parts):
            break
        entries.extend(parts)
        j += 1
        if tokens[j - 1].ends_sentence:
            break
    value = words_to_number(entries) if entries else None
    return (value, j) if value is not None and 1 <= value < 1000 else None


def _number_runs(tokens: list[_Token]) -> list[tuple[int, int, int]]:
    """Tramos de tokens que forman una altura: (inicio, fin exclusivo, número)."""
    runs: list[tuple[int, int, int]] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.kind == "num":
            value = int(tok.text.replace(".", ""))
            end = i + 1
            if end < len(tokens) and tokens[end].kind == "word" and tokens[end].folded == "mil" and value < 100:
                # "2 mil", "2 mil 500", "2 mil quinientos".
                value, end = value * 1000, end + 1
                rest = _mil_remainder(tokens, end)
                if rest:
                    value, end = value + rest[0], rest[1]
            if 1 <= value <= _MAX_NUMBER:
                runs.append((i, end, value))
            i = end
            continue
        if tok.kind != "word" or _number_word(tok.text) is None:
            i += 1
            continue
        entries: list[tuple[str, int]] = []
        j = i
        while j < len(tokens):
            t = tokens[j]
            if t.kind != "word":
                break
            if t.folded == "y" and entries and j + 1 < len(tokens):
                nxt = tokens[j + 1]
                if nxt.kind == "word" and _number_word(nxt.text):
                    entries.append(("y", 0))
                    j += 1
                    continue
                break
            parts = _number_word(t.text)
            if parts is None:
                break
            entries.extend(parts)
            j += 1
            if t.ends_sentence:
                break
        number = words_to_number(entries)
        if number is not None:
            runs.append((i, j, number))
        i = j
    return runs


def _street_before(tokens: list[_Token], run_start: int) -> list[_Token] | None:
    """El nombre de la calle que termina justo antes de la altura, o None."""
    i = run_start - 1
    skipped = 0
    while i >= 0 and skipped < 2 and (
        tokens[i].kind == "sign" or (tokens[i].kind == "word" and tokens[i].folded in _BEFORE_NUMBER)
    ):
        if tokens[i].ends_sentence and tokens[i].folded not in _ABBREVIATIONS:
            return None
        i -= 1
        skipped += 1

    street: list[_Token] = []
    anchored = False
    while i >= 0 and len(street) < 6:
        tok = tokens[i]
        if tok.kind == "punct" or tok.ends_sentence:
            anchored = True
            break
        folded = tok.folded
        if tok.kind == "word" and folded in _PREPOSITIONS:
            anchored = True
            break
        if tok.kind == "word" and folded in _NOT_STREET:
            break
        street.insert(0, tok)
        if folded in _STREET_TYPES:
            anchored = True
            break
        i -= 1
    else:
        anchored = anchored or i < 0

    if not anchored:
        # Sin "en", "calle" ni comienzo de texto: aceptar solo un nombre propio con mayúscula.
        tail: list[_Token] = []
        for tok in reversed(street):
            if tok.text[:1].isupper() or tok.folded in _CONNECTORS or tok.kind == "num":
                tail.insert(0, tok)
            else:
                break
        while tail and not tail[0].text[:1].isupper():
            tail.pop(0)
        street = tail

    while street and street[0].folded in {"de", "del", "y"}:
        street.pop(0)
    has_name = any(
        t.kind == "word"
        and t.folded not in _STREET_TYPES
        and t.folded not in _CONNECTORS
        and _number_word(t.text) is None
        and len(t.folded) >= 3
        for t in street
    )
    return street if has_name else None


_CORNER = {"y", "esquina", "esq"}
_BETWEEN = "entre"


def _street_after(tokens: list[_Token], start: int) -> list[_Token] | None:
    """Nombre de calle que empieza en `start`: con mayúscula (o tipo de calle) y sin verbos ni "local"."""
    street: list[_Token] = []
    i = start
    while i < len(tokens) and len(street) < 6:
        tok = tokens[i]
        if tok.kind not in {"word", "num"}:
            break
        folded = tok.folded
        if folded in _NOT_STREET or folded in _PREPOSITIONS or folded in _CORNER or folded == _BETWEEN:
            break
        if not street and not (tok.text[:1].isupper() or folded in _STREET_TYPES or tok.kind == "num"):
            return None
        if street and not (tok.text[:1].isupper() or folded in _CONNECTORS or folded in _STREET_TYPES):
            break
        street.append(tok)
        if tok.ends_sentence:
            break
        i += 1
    while street and street[-1].folded in _CONNECTORS:
        street.pop()
    has_name = any(
        t.kind == "word" and t.folded not in _STREET_TYPES and t.folded not in _CONNECTORS and len(t.folded) >= 3
        for t in street
    )
    return street if has_name else None


def _is_barrio(tokens: list[_Token]) -> bool:
    return barrio_por_variante(" ".join(t.text for t in tokens)) is not None and tokens[0].folded not in _STREET_TYPES


def _corner(text: str, tokens: list[_Token]) -> ParsedAddress | None:
    for k, tok in enumerate(tokens):
        if tok.kind != "word" or tok.folded not in _CORNER | {_BETWEEN} or k == 0:
            continue
        first = _street_before(tokens, k)
        # "en la esquina de Corrientes y Callao": la calle empieza después de "esquina de".
        while first and (first[0].folded in _CONNECTORS or first[0].folded in _CORNER):
            first.pop(0)
        second = _street_after(tokens, k + 1)
        if not first or not second:
            continue
        if not first[0].text[:1].isupper() and first[0].folded not in _STREET_TYPES:
            continue
        if _is_barrio(first) or _is_barrio(second):  # "en Palermo y Belgrano" son dos barrios
            continue
        end_token = second[-1]
        approximate = tok.folded == _BETWEEN
        if approximate:
            # "A entre B y C": hace falta la segunda calle para que sea "entre calles".
            j = k + 1 + len(second)
            if j >= len(tokens) or tokens[j].folded != "y" or not _street_after(tokens, j + 1):
                continue
            end_token = _street_after(tokens, j + 1)[-1]
        first_text = " ".join(t.text for t in first)
        second_text = " ".join(t.text for t in second)
        return ParsedAddress(
            raw_text=" ".join(text[first[0].start : end_token.end].split()),
            address=f"{first_text} y {second_text}",
            street=first_text,
            number=0,
            start=first[0].start,
            end=end_token.end,
            cross_street=second_text,
            approximate=approximate,
        )
    return None


def _alternative_height(tokens: list[_Token], end: int, runs: list[tuple[int, int, int]]) -> bool:
    """True si después de la altura viene otra con "o" / "u" ("2000 o 2500", "al 2 mil o 2500")."""
    if end >= len(tokens) or tokens[end].folded not in {"o", "u"} or tokens[end - 1].ends_sentence:
        return False
    return any(start == end + 1 for start, _e, _n in runs)


def extract_address(text: str) -> ParsedAddress | None:
    """Busca la primera "calle + altura" de un texto; si no hay, una esquina. None si no hay ninguna."""
    if not text:
        return None
    tokens = _tokenize(text)
    runs = _number_runs(tokens)
    for start, end, number in runs:
        after = tokens[end] if end < len(tokens) else None
        if after and after.kind == "word" and after.folded in _NOT_HEIGHT_AFTER:
            continue
        street = _street_before(tokens, start)
        if not street:
            continue
        street_text = " ".join(t.text for t in street)
        raw_end = tokens[end - 1].end
        return ParsedAddress(
            raw_text=" ".join(text[street[0].start : raw_end].split()),
            address=f"{street_text} {number}",
            street=street_text,
            number=number,
            start=street[0].start,
            end=raw_end,
            # "Monroe 2000 o 2500": se usa la primera altura.
            approximate=_alternative_height(tokens, end, runs),
        )
    return _corner(text, tokens)


def normalize_address(address: str | None) -> str | None:
    """Pasa a cifras la altura que el LLM devuelva en palabras ("Monroe dos mil", "Monroe 2 mil") y
    deja una sola altura si trae dos ("Monroe 2000 o 2500"). Lo demás queda igual."""
    if not address:
        return address
    parsed = extract_address(address)
    if parsed is None:
        return address
    if re.search(r"\d", address) and not re.search(r"\d\s*mil\b", _fold(address)) and not parsed.approximate:
        # Ya tiene cifras ("Av. Corrientes 2.500", "Gorriti 4500, Palermo"): USIG la entiende así.
        return address
    return parsed.address
