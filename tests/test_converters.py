import pytest
from datetime import date, datetime, time
from app.utils.converters import (
    coerce_float,
    coerce_int,
    coerce_string,
    coerce_date_or_none,
    coerce_date_or_today,
    coerce_time,
    coerce_datetime
)

def test_coerce_float():
    assert coerce_float("150,5") == 150.5
    assert coerce_float("150.5") == 150.5
    assert coerce_float(100) == 100.0
    assert coerce_float("") is None
    assert coerce_float("abc") is None
    assert coerce_float(None) is None

def test_coerce_int():
    assert coerce_int("150,5") == 150
    assert coerce_int("150.5") == 150
    assert coerce_int(100) == 100
    assert coerce_int("") is None
    assert coerce_int("abc") is None
    assert coerce_int(None) is None

def test_coerce_string():
    assert coerce_string("  teste  ") == "teste"
    assert coerce_string(None) == ""
    assert coerce_string(123) == "123"

def test_coerce_date():
    assert coerce_date_or_none("2024-01-01") == date(2024, 1, 1)
    assert coerce_date_or_none("data ruim") is None
    assert coerce_date_or_today("bad_date") == date.today()

def test_coerce_time():
    assert coerce_time("14:30") == time(14, 30)
    assert coerce_time("14:30:00") == time(14, 30)
    assert coerce_time("hora_zoada") is None

def test_coerce_datetime():
    dt = coerce_datetime("2024-01-01T14:30:00Z")
    assert isinstance(dt, datetime)
    assert dt.year == 2024
    assert coerce_datetime("lixo") is None
