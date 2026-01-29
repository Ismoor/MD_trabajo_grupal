# iata_client.py
from typing import Optional, Dict, Any
import os
import requests

API_BASE_URL = "https://www.air-port-codes.com"

# 🔐 Leer desde variables de entorno
API_KEY = os.getenv("AIRPORT_CODES_API_KEY")
API_SECRET = os.getenv("AIRPORT_CODES_API_SECRET")

class IataLookupError(Exception):
    pass


def get_iata_code(city_name: Optional[str], debug: bool = False) -> Optional[str]:
    if not city_name:
        return None

    if not API_KEY or not API_SECRET:
        raise IataLookupError(
            "API Key o API Secret no definidos. "
            "Configure las variables de entorno AIRPORT_CODES_API_KEY y AIRPORT_CODES_API_SECRET."
        )

    url = f"{API_BASE_URL}/api/v1/multi"
    headers = {
        "APC-Auth": API_KEY,
        "APC-Auth-Secret": API_SECRET
    }

    payload = {"term": city_name}

    try:
        r = requests.post(url, headers=headers, data=payload, timeout=15)
        if debug:
            print("DEBUG status:", r.status_code)
            print("DEBUG body:", r.text[:400])
        r.raise_for_status()
        data: Dict[str, Any] = r.json()
    except Exception as e:
        raise IataLookupError(f"Fallo consultando IATA para '{city_name}': {e}")

    airports = data.get("airports", [])
    if not airports:
        return None

    iata = airports[0].get("iata")
    if isinstance(iata, str) and len(iata.strip()) == 3:
        return iata.strip().upper()

    return None
