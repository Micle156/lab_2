from datetime import UTC, datetime

import pytest

from streamstats.errors import (
    UncorrectedEventsError,
    UncorrectTimeError,
    UnSupportedFormatError,
)
from streamstats.parsers import make_csv, make_else

"""корректные тесты"""

def test_csv_1():
    f = "2026-01-01T05:00:00+00:00,INFO,SRC,MES\n"
    number = 2
    event = make_csv(f, number)
    assert event["timestamp"] == datetime(
        2026, 1, 1, 5, 0, 0, tzinfo=UTC
    )
    assert event["level"] == "INFO"
    assert event["source"] == "SRC"
    assert event["message"] == "MES"

def test_csv_2():
    f = "2026-01-01T05:00:00+00:00,DEBUG,SRC,\n"
    number = 2
    event = make_csv(f, number)
    assert event["timestamp"] == datetime(
        2026, 1, 1, 5, 0, 0, tzinfo=UTC
    )
    assert event["level"] == "DEBUG"
    assert event["source"] == "SRC"
    assert event["message"] == ""

def test_csv_3():
    f = "2026-01-01T05:00:00+00:00,ERROR,источник,привет\n"
    number = 2
    event = make_csv(f, number)
    assert event["timestamp"] == datetime(
        2026, 1, 1, 5, 0, 0, tzinfo=UTC
    )
    assert event["level"] == "ERROR"
    assert event["source"] == "источник"
    assert event["message"] == "привет"

"""некорректные тесты"""

def test_csv_4():
    with pytest.raises(UncorrectedEventsError):
        f = "2026-01-01T05:00:00+00:00,CRITICAL,источник\n"
        make_csv(f, number = 2)

def test_csv_5():
    with pytest.raises(UncorrectedEventsError):
        f = "2026-01-01T05:00:00+00:00,уровень,источник,\n"
        make_csv(f, number = 2)

def test_csv_6():
    with pytest.raises(UncorrectTimeError):
        f = ",ERROR,SRC,\n"
        make_csv(f, number = 2)

def test_csv_7():
    with pytest.raises(UncorrectTimeError):
        f = "10:2:4 14.12.2007,ERROR,src,\n"
        make_csv(f, number = 2)

def test_csv_8():
    with pytest.raises(UncorrectedEventsError):
        f = "2026-01-01T05:00:00+00:00,CRITICAL,источник,MES,E\n"
        make_csv(f, number = 2)

def test_csv_9():
    with pytest.raises(UncorrectedEventsError):
        f = "2026-01-01T05:00:00+00:00,уровень,,\n"
        make_csv(f, number = 2)

def test_csv_10():
    with pytest.raises(UncorrectTimeError):
        f = "MES,2026-01-01T05:00:00+00:00,ERROR,SRC\n"
        make_csv(f, number = 2)

def test_csv_11():
    with pytest.raises(UnSupportedFormatError):
            make_else(frmt = "txt")