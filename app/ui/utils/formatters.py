import re

def format_phone(text: str) -> str:
    raw = re.sub(r"\D", "", text)[:11]

    if not raw:
        return ""
    elif len(raw) == 1:
        return f"({raw}"
    elif len(raw) == 2:
        return f"({raw})"
    elif len(raw) <= 7:
        return f"({raw[:2]}) {raw[2:]}"
    else:
        # Dinâmico para 10 ou 11 dígitos
        if len(raw) <= 10:
            return f"({raw[:2]}) {raw[2:6]}-{raw[6:]}"
        else:
            return f"({raw[:2]}) {raw[2:7]}-{raw[7:]}"

def format_date_br(text: str) -> str:
    raw = re.sub(r"\D", "", text)
    if len(raw) > 8:
        raw = raw[:8]
    parts = []
    if len(raw) >= 2:
        parts.append(raw[:2])
    if len(raw) >= 4:
        parts.append(raw[2:4])
    if len(raw) > 4:
        parts.append(raw[4:])
    return "/".join(parts)
