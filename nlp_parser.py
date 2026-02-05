# nlp_parser.py
import re
from typing import Optional, Dict, Tuple

_NUM_MAP = {
    "un": 1, "uno": 1, "una": 1,
    "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
}

_MONTHS = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre"

_KNOWN_AIRLINES = ["Iberia", "Lufthansa", "Avianca", "LATAM", "Latam", "AirEuropa", "Air Europa"]

_CITY_STOPWORDS = {
    "el", "la", "los", "las", "para", "en", "con", "del", "al", "de", "desde", "a",
    "un", "una", "uno",
    "necesito", "quiero", "comprar", "compra", "billete", "billetes", "pasaje", "pasajes",
    "boleto", "boletos", "ticket", "tickets", "barato", "barata"
}

_COUNTRY_ALIASES = {
    "ecuador": "EC",
    "espana": "ES", "españa": "ES",
    "italia": "IT",
    "colombia": "CO",
    "venezuela": "VE",
    "australia": "AU",
    "palau": "PW",
    "estados unidos": "US", "usa": "US",
    "mexico": "MX", "méxico": "MX",
    "peru": "PE", "perú": "PE",
    "argentina": "AR",
    "chile": "CL",
    "brasil": "BR"
}

def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())

def _title_case(text: str) -> str:
    text = _clean_text(text)
    return " ".join(w[:1].upper() + w[1:].lower() if w else w for w in text.split(" "))

def _extract_date_and_remove(msg: str) -> Tuple[Optional[str], str]:
    m0 = re.search(r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b", msg)
    if m0:
        fecha = f"{m0.group(1)}-{m0.group(2)}-{m0.group(3)}"
        msg = msg[:m0.start()] + " " + msg[m0.end():]
        return fecha, _clean_text(msg)

    pattern_es = rf"\b(\d{{1,2}})\s+de\s+({_MONTHS})(?:\s+de\s+(\d{{4}}))?\b"
    m = re.search(pattern_es, msg, re.IGNORECASE)
    if m:
        day, month, year = m.group(1), m.group(2).lower(), m.group(3)
        fecha = f"{day} de {month}" + (f" de {year}" if year else "")
        msg = msg[:m.start()] + " " + msg[m.end():]
        return fecha, _clean_text(msg)

    m2 = re.search(rf"\b(?:en|para)\s+({_MONTHS})\b", msg, re.IGNORECASE)
    if m2:
        month = m2.group(1).lower()
        msg = msg[:m2.start()] + " " + msg[m2.end():]
        return month, _clean_text(msg)

    return None, msg

def _extract_airline(msg: str) -> Optional[str]:
    m = re.search(r"\bcon\s+([a-z0-9áéíóúñ][a-z0-9áéíóúñ\s\.-]{1,40})", msg, re.IGNORECASE)
    if m:
        airline = m.group(1).strip()
        airline = re.split(r"\b(de|desde|a|para|el|la|los|las|en)\b", airline, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        airline = _title_case(airline)
        return airline if airline else None

    for a in _KNOWN_AIRLINES:
        if re.search(rf"\b{re.escape(a)}\b", msg, re.IGNORECASE):
            return a.replace("Air Europa", "AirEuropa")

    return None

def _remove_airline_from_text(msg: str, airline: Optional[str]) -> str:
    if not airline:
        return msg
    msg = re.sub(rf"\bcon\s+{re.escape(airline)}\b", " ", msg, flags=re.IGNORECASE)
    msg = re.sub(rf"\b{re.escape(airline)}\b", " ", msg, flags=re.IGNORECASE)
    return _clean_text(msg)

def _extract_quantity(msg: str) -> Optional[str]:
    keywords = r"(?:billetes?|pasajes?|tickets?|personas?|boletos?)"
    m = re.search(rf"\b(\d{{1,2}})\b\s*{keywords}\b", msg, re.IGNORECASE)
    if m:
        return str(int(m.group(1)))

    m2 = re.search(r"\b(" + "|".join(_NUM_MAP.keys()) + rf")\b\s*{keywords}\b", msg, re.IGNORECASE)
    if m2:
        return str(_NUM_MAP[m2.group(1).lower()])

    return None

def _clean_city_phrase(s: str) -> Optional[str]:
    if not s:
        return None

    s = _clean_text(s)
    tokens = [t for t in s.split(" ") if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\-]+", t)]
    if not tokens:
        return None

    while tokens and tokens[0].lower() in _CITY_STOPWORDS:
        tokens.pop(0)
    while tokens and tokens[-1].lower() in _CITY_STOPWORDS:
        tokens.pop()

    if not tokens:
        return None

    return _title_case(" ".join(tokens[:3]))

def _extract_route(msg: str) -> Tuple[Optional[str], Optional[str]]:
    pattern_full = r"(?:de|desde)\s+(.+?)\s+\ba\b\s+(.+)"
    m = re.search(pattern_full, msg, re.IGNORECASE)
    if m:
        return _clean_city_phrase(m.group(1)), _clean_city_phrase(m.group(2))

    pattern_simple = r"(.+?)\s+\ba\b\s+(.+)"
    m2 = re.search(pattern_simple, msg, re.IGNORECASE)
    if m2:
        return _clean_city_phrase(m2.group(1)), _clean_city_phrase(m2.group(2))

    return None, None

def _extract_country_after_city(msg: str, city: Optional[str]) -> Optional[str]:
    if not msg or not city:
        return None

    city_esc = re.escape(city)

    m = re.search(rf"\b{city_esc}\b\s*(?:,|-)\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+)", msg, re.IGNORECASE)
    if m:
        country = _clean_text(m.group(1)).lower()
        country = re.split(r"\b(para|en|con|el|la|los|las|del|al|de)\b", country, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        return _COUNTRY_ALIASES.get(country)

    m2 = re.search(rf"\b{city_esc}\b\s*\(\s*([^)]+)\s*\)", msg, re.IGNORECASE)
    if m2:
        country = _clean_text(m2.group(1)).lower()
        country = re.split(r"\b(para|en|con|el|la|los|las|del|al|de)\b", country, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        return _COUNTRY_ALIASES.get(country)

    return None

def parse_user_message(message: str) -> Dict[str, Optional[str]]:
    msg = _clean_text(message)

    fecha, msg = _extract_date_and_remove(msg)

    aerolinea = _extract_airline(msg)
    msg = _remove_airline_from_text(msg, aerolinea)

    cantidad = _extract_quantity(msg)
    origen, destino = _extract_route(msg)

    origen_iso = _extract_country_after_city(message, origen)
    destino_iso = _extract_country_after_city(message, destino)

    return {
        "origen": origen,
        "destino": destino,
        "fecha": fecha,
        "cantidad": cantidad if cantidad is not None else "1",
        "aerolínea": aerolinea,
        "origen_iso": origen_iso,
        "destino_iso": destino_iso
    }