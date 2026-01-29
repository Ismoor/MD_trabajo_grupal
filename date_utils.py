# date_utils.py
from __future__ import annotations
from typing import Optional
import re

_MONTH_TO_NUM = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9,
    "octubre": 10, "noviembre": 11, "diciembre": 12
}

def normalize_date_es(date_text: Optional[str], default_year: int) -> Optional[str]:
    """
    Convierte:
      - '15 de octubre' -> '15-10-<default_year>'
      - '15 de octubre de 2026' -> '15-10-2026'
    Retorna None si no reconoce formato.
    """
    if not date_text:
        return None

    s = date_text.strip().lower()

    # formato dd-mm-yyyy ya listo
    m0 = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{4})", s)
    if m0:
        d, mo, y = int(m0.group(1)), int(m0.group(2)), int(m0.group(3))
        if 1 <= d <= 31 and 1 <= mo <= 12:
            return f"{d:02d}-{mo:02d}-{y:04d}"
        return None

    # formato "15 de octubre" o "15 de octubre de 2026"
    m = re.fullmatch(r"(\d{1,2})\s+de\s+([a-záéíóúñ]+)(?:\s+de\s+(\d{4}))?", s)
    if not m:
        return None

    day = int(m.group(1))
    month_name = m.group(2)
    year = int(m.group(3)) if m.group(3) else int(default_year)

    month = _MONTH_TO_NUM.get(month_name)
    if not month:
        return None

    if not (1 <= day <= 31):
        return None

    return f"{day:02d}-{month:02d}-{year:04d}"