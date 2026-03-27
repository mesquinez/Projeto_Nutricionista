from datetime import date, datetime, time
from typing import Optional

def coerce_float(val) -> Optional[float]:
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val.replace(',', '.'))
        except (ValueError, TypeError):
            return None
    return None

def coerce_int(val) -> Optional[int]:
    if val is None or val == "":
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, (float, str)):
        try:
            return int(float(str(val).replace(',', '.')))
        except (ValueError, TypeError):
            return None
    return None

def coerce_string(val) -> str:
    return str(val).strip() if val is not None else ""

def coerce_date_or_none(val) -> Optional[date]:
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            return date.fromisoformat(val[:10])
        except (ValueError, TypeError):
            return None
    return None

def coerce_date_or_today(val) -> date:
    d = coerce_date_or_none(val)
    return d if d is not None else date.today()

def coerce_time(val) -> Optional[time]:
    if isinstance(val, time):
        return val
    if isinstance(val, str):
        try:
            return time.fromisoformat(val[:8])
        except (ValueError, TypeError):
            return None
    return None

def coerce_datetime(val) -> Optional[datetime]:
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            clean_str = val.replace("Z", "+00:00").replace(" ", "T")
            return datetime.fromisoformat(clean_str)
        except (ValueError, TypeError):
            return None
    return None
