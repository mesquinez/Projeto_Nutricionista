import re

def is_valid_number(text: str) -> bool:
    if not text:
        return True # Optional fields handle empty elsewhere
    # Allow comma or dot
    clean = text.replace(',', '.')
    try:
        float(clean)
        return True
    except ValueError:
        return False

def is_valid_int(text: str) -> bool:
    if not text:
        return True
    try:
        int(text)
        return True
    except ValueError:
        return False
