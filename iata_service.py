# iata_service.py
from typing import Dict, Any, Optional, Tuple
from geopy.geocoders import Nominatim

from iata_client import get_iata_code
from date_utils import normalize_date_es

geolocator = Nominatim(user_agent="asistente_vuelos_2026")


def get_smart_location(city_text: Optional[str], iso_hint: Optional[str] = None, language: str = "es") -> Tuple[Optional[str], Optional[str]]:
    """
    Resuelve la ciudad a un nombre más limpio y un ISO de país usando Nominatim.
    iso_hint ayuda a desambiguar (ej: 'Roma' + 'IT').
    """
    if not city_text:
        return None, None

    query = f"{city_text}, {iso_hint}" if iso_hint else city_text

    try:
        loc = geolocator.geocode(query, language=language, addressdetails=True, timeout=10)
        if not loc:
            return city_text, iso_hint

        addr = loc.raw.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("state") or city_text
        iso = (addr.get("country_code") or "").upper() or iso_hint
        return city, iso
    except Exception:
        return city_text, iso_hint


def build_final_json(parsed: Dict[str, Optional[str]]) -> Dict[str, Any]:
    origen_txt = parsed.get("origen")
    destino_txt = parsed.get("destino")

    # ISO extraído por el parser si el usuario lo dio
    iso_origen_hint = parsed.get("origen_iso")
    iso_destino_hint = parsed.get("destino_iso")

    # Nombre para mostrar (español)
    origen_es, iso_origen = get_smart_location(origen_txt, iso_hint=iso_origen_hint, language="es")
    destino_es, iso_destino = get_smart_location(destino_txt, iso_hint=iso_destino_hint, language="es")

    # Nombre para consultar IATA (inglés)
    origen_en, _ = get_smart_location(origen_txt, iso_hint=iso_origen, language="en")
    destino_en, _ = get_smart_location(destino_txt, iso_hint=iso_destino, language="en")

    iata_from = get_iata_code(origen_en, preferred_isos=[iso_origen] if iso_origen else None)
    iata_to = get_iata_code(destino_en, preferred_isos=[iso_destino] if iso_destino else None)

    pax = int(parsed.get("cantidad") or "1")

    return {
        "Ciudad Origen": origen_es,
        "Ciudad Destino": destino_es,
        "IATA From": iata_from,
        "IATA To": iata_to,
        "Fecha": normalize_date_es(parsed.get("fecha")),
        "Pax": pax,
        "Aerolínea": parsed.get("aerolínea"),
    }