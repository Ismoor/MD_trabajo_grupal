# iata_service.py
from typing import Dict, Any, Optional


def postprocess_entities(parsed: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Aplica reglas del enunciado / avance:
    - Si falta fecha o aerolínea -> None
    - Si falta cantidad -> '1'
    - cantidad debe quedar como string numérico
    """
    origen = parsed.get("origen")
    destino = parsed.get("destino")
    fecha = parsed.get("fecha") if parsed.get("fecha") else None
    aerolinea = parsed.get("aerolínea") if parsed.get("aerolínea") else None

    cantidad_raw = parsed.get("cantidad")
    if not cantidad_raw:
        cantidad = "1"
    else:
        try:
            cantidad = str(int(cantidad_raw))
        except ValueError:
            cantidad = "1"

    return {
        "origen": origen,
        "destino": destino,
        "fecha": fecha,
        "cantidad": cantidad,
        "aerolínea": aerolinea
    }
