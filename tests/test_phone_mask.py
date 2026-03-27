from app.ui.utils.formatters import format_date_br, format_phone

def test_format_phone_empty():
    assert format_phone("") == ""

def test_format_phone_partial():
    assert format_phone("2") == "(2"
    assert format_phone("21") == "(21)"
    assert format_phone("219") == "(21) 9"
    assert format_phone("219999") == "(21) 9999"

def test_format_phone_complete():
    assert format_phone("21999998888") == "(21) 99999-8888"
    assert format_phone("2133334444") == "(21) 3333-4444"

def test_format_phone_invalid_chars():
    assert format_phone("21a99b999c8888") == "(21) 99999-8888"

def test_format_phone_paste():
    assert format_phone("(21) 99999-8888") == "(21) 99999-8888"
    assert format_phone("21 99999 8888") == "(21) 99999-8888"

def test_format_phone_max_length():
    assert format_phone("21999998888123") == "(21) 99999-8888"


def test_format_date_partial():
    assert format_date_br("1") == "1"
    assert format_date_br("12") == "12"
    assert format_date_br("123") == "12/3"
    assert format_date_br("1234") == "12/34"


def test_format_date_complete_and_paste():
    assert format_date_br("12345678") == "12/34/5678"
    assert format_date_br("12/03/1990") == "12/03/1990"
    assert format_date_br("12031990123") == "12/03/1990"
