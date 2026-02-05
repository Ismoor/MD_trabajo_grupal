# date_utils.py
from typing import Optional
import re
from datetime import date
import unicodedata

_MONTH_TO_NUM = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9,
    "octubre": 10, "noviembre": 11, "diciembre": 12
}

def _strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def normalize_date_es(date_text: Optional[str]) -> Optional[str]:
    """Devuelve fecha en formato dd-mm-yyyy, soporta: dd-mm-yyyy, '15 de octubre', 'septiembre'."""
    if not date_text:
        return None

    s = _strip_accents(date_text.strip().lower())
    today = date.today()

    m0 = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{4})", s)
    if m0:
        d, m, y = map(int, m0.groups())
        return f"{d:02d}-{m:02d}-{y:04d}"

    if re.fullmatch(r"[a-z]+", s):
        month = _MONTH_TO_NUM.get(s)
        if not month:
            return None
        year = today.year + (1 if month < today.month else 0)
        return f"01-{month:02d}-{year}"

    m = re.fullmatch(r"(\d{1,2})\s+de\s+([a-z]+)(?:\s+de\s+(\d{4}))?", s)
    if not m:
        return None

    day = int(m.group(1))
    month_name = m.group(2)
    year_txt = m.group(3)

    month = _MONTH_TO_NUM.get(month_name)
    if not month:
        return None

    year = int(year_txt) if year_txt else (today.year + (1 if (month, day) < (today.month, today.day) else 0))
    return f"{day:02d}-{month:02d}-{year}"