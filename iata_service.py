# iata_service.py
from __future__ import annotations
from typing import Dict, Any, Optional
from datetime import datetime

from date_utils import normalize_date_es
from iata_client import get_iata_code, IataLookupError

def build_final_json(parsed: Dict[str, Optional[str]]) -> Dict[str, Any]:
    origen = parsed.get("origen")
    destino = parsed.get("destino")

    # Pax: si no viene, default 1
    pax_raw = parsed.get("cantidad")
    try:
        pax = int(pax_raw) if pax_raw else 1
    except ValueError:
        pax = 1

    # Fecha: normalizar
    current_year = datetime.now().year
    fecha_norm = normalize_date_es(parsed.get("fecha"), default_year=current_year)

    # IATA lookup (si falla, queda None)
    iata_from = None
    iata_to = None
    try:
        iata_from = get_iata_code(origen)
        iata_to = get_iata_code(destino)
    except IataLookupError:
        # no revienta el bot; solo deja None
        pass

    return {
        "Ciudad Origen": origen,           # string
        "Ciudad Destino": destino,         # string
        "IATA From": iata_from,            # string 3 o None
        "IATA To": iata_to,                # string 3 o None
        "Fecha": fecha_norm,               # dd-mm-yyyy o None
        "Pax": pax                         # int
    }
