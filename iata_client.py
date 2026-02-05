# iata_client.py
from typing import Optional, Dict, Any, List
import os
import requests

API_BASE_URL = "https://www.air-port-codes.com"
API_KEY = os.getenv("AIRPORT_CODES_API_KEY")
API_SECRET = os.getenv("AIRPORT_CODES_API_SECRET")


class IataLookupError(Exception):
    pass


def has_credentials() -> bool:
    return bool(API_KEY and API_SECRET)


def _country_iso(ap: Dict[str, Any]) -> Optional[str]:
    c = ap.get("country")
    if isinstance(c, dict):
        iso = c.get("iso")
        return iso.upper() if isinstance(iso, str) and len(iso) == 2 else None
    return None


def _is_all_airports(ap: Dict[str, Any]) -> bool:
    name = ap.get("name")
    return isinstance(name, str) and "all airports" in name.lower()


def _pick_best_airport(airports: List[Dict[str, Any]], preferred_isos: Optional[List[str]] = None) -> Optional[str]:
    """Elige el mejor IATA: filtra por país si se puede, prefiere 'All Airports', si no el primero."""
    def valid_iata(ap):
        iata = ap.get("iata")
        return isinstance(iata, str) and len(iata.strip()) == 3

    pool = [ap for ap in airports if valid_iata(ap)]
    if not pool:
        return None

    if preferred_isos:
        isos = [x.upper() for x in preferred_isos if x]
        filtered = [ap for ap in pool if _country_iso(ap) in isos]
        if filtered:
            pool = filtered

    for ap in pool:
        if _is_all_airports(ap):
            return ap["iata"].strip().upper()

    return pool[0]["iata"].strip().upper()


def get_iata_code(city_name: Optional[str], preferred_isos: Optional[List[str]] = None) -> Optional[str]:
    """Consulta la API y devuelve un IATA de 3 letras o None."""
    if not city_name or not has_credentials():
        return None

    url = f"{API_BASE_URL}/api/v1/multi"
    headers = {"APC-Auth": API_KEY, "APC-Auth-Secret": API_SECRET}
    payload = {"term": city_name}

    try:
        r = requests.post(url, headers=headers, data=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise IataLookupError(f"Error IATA para '{city_name}': {e}")

    airports = data.get("airports", [])
    if not isinstance(airports, list) or not airports:
        return None

    return _pick_best_airport(airports, preferred_isos=preferred_isos)