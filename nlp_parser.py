# nlp_parser.py
import re
from typing import Optional, Dict, Tuple

_NUM_MAP = {
    "un": 1, "uno": 1, "una": 1,
    "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
}

_MONTHS = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre"


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _title_case(text: str) -> str:
    text = _clean_text(text)
    return " ".join([w[:1].upper() + w[1:].lower() if w else w for w in text.split(" ")])


def _extract_date_and_remove(msg: str) -> Tuple[Optional[str], str]:
    """
    Extrae: '15 de octubre' o '15 de octubre de 2026'
    y lo elimina del texto para no confundir el 'de' con la ruta.
    """
    pattern = rf"\b(\d{{1,2}})\s+de\s+({_MONTHS})(?:\s+de\s+(\d{{4}}))?\b"
    m = re.search(pattern, msg, re.IGNORECASE)
    if not m:
        return None, msg

    day, month, year = m.group(1), m.group(2).lower(), m.group(3)
    fecha = f"{day} de {month}" + (f" de {year}" if year else "")
    msg_removed = msg[:m.start()] + " " + msg[m.end():]
    return fecha, _clean_text(msg_removed)


def _extract_airline(msg: str) -> Optional[str]:
    """
    'con Iberia' -> 'Iberia'
    """
    m = re.search(r"\bcon\s+([a-z0-9áéíóúñ][a-z0-9áéíóúñ\s\.-]{1,40})", msg, re.IGNORECASE)
    if not m:
        return None

    airline = m.group(1).strip()
    airline = re.split(r"\b(de|desde|a|para|el|la|los|las)\b", airline, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    return _title_case(airline) if airline else None


def _extract_quantity(msg: str) -> Optional[str]:
    """
    Cantidad SOLO si está vinculada a billetes/pasajes/tickets/personas.
    Evita agarrar el '15' de la fecha.
    """
    m = re.search(r"\b(\d{1,2})\b\s*(?:billetes?|pasajes?|tickets?|personas?)\b", msg, re.IGNORECASE)
    if m:
        return str(int(m.group(1)))

    m2 = re.search(r"\b(" + "|".join(_NUM_MAP.keys()) + r")\b\s*(?:billetes?|pasajes?|tickets?|personas?)\b", msg, re.IGNORECASE)
    if m2:
        return str(_NUM_MAP[m2.group(1).lower()])

    return None  # si no se menciona, lo maneja el post-proceso


def _extract_route(msg: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Busca 'de <origen> a <destino>' o 'desde <origen> a <destino>'.
    Toma la última coincidencia (la ruta real suele estar al final).
    """
    city = r"[a-záéíóúñ]+(?:\s+[a-záéíóúñ]+)*"
    pattern = rf"\b(?:de|desde)\s+({city})\s+\ba\b\s+({city})\b"
    matches = list(re.finditer(pattern, msg, re.IGNORECASE))
    if not matches:
        return None, None

    m = matches[-1]
    return _title_case(m.group(1)), _title_case(m.group(2))


def parse_user_message(message: str) -> Dict[str, Optional[str]]:
    """
    Devuelve el JSON intermedio pedido:
    {
      'origen': 'Quito',
      'destino': 'Madrid',
      'fecha': '15 de octubre' o None,
      'cantidad': '3' o None,
      'aerolínea': 'Iberia' o None
    }
    """
    msg = _clean_text(message)

    fecha, msg_wo_date = _extract_date_and_remove(msg)
    aerolinea = _extract_airline(msg_wo_date)
    cantidad = _extract_quantity(msg_wo_date)
    origen, destino = _extract_route(msg_wo_date)

    return {
        "origen": origen,
        "destino": destino,
        "fecha": fecha,
        "cantidad": cantidad,
        "aerolínea": aerolinea
    }