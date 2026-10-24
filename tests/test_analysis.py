"""тест UNIT в analysis нет проверки ошибок
   проверка только корректных тестов"""

from datetime import UTC, datetime

from streamstats.analysis import top, update_stat


def make_stat():
    return {
    "total": 0,
    "st_level": {
        "CRITICAL": 0,
        "DEBUG": 0,
        "ERROR": 0,
        "INFO": 0,
        "WARNING": 0
    },
    "st_source": {},
    "first_timestamp": None,
    "last_timestamp": None,
    "skip": 0
    }

def make_dict(ts, level, source, mes):
    return {
        "timestamp": datetime.fromisoformat(ts),
        "level": level,
        "source": source,
        "message": mes
    }

def test_analis_1():
    stat = make_stat()
    ts = '2025-12-14T01:12:11+00:00'
    level = "ERROR"
    source = "SRC"
    mes = ""
    update_stat(make_dict(ts, level, source, mes), stat)
    assert stat["total"] == 1
    assert stat["st_source"]["SRC"] == {"total": 1, "error": 1}
    assert stat["skip"] == 0

def test_analis_2():
    stat = make_stat()
    ts = "2024-12-14T01:12:11+00:00"
    level = "ERROR"
    source = "SRC"
    mes = ""
    update_stat(make_dict(ts, level, source, mes), stat)
    ts = "2025-12-14T01:12:11+00:00"
    level = "INFO"
    source = "SRC"
    mes = "message"
    update_stat(make_dict(ts, level, source, mes), stat)
    assert stat["total"] == 2
    assert stat["first_timestamp"] == datetime(
        2024, 12, 14, 1, 12, 11, tzinfo=UTC
    )
    assert stat["last_timestamp"] == datetime(
            2025, 12, 14, 1, 12, 11, tzinfo=UTC
    )
    assert stat["st_source"]["SRC"] == {"total": 2, "error": 1}
    assert stat["st_level"]["INFO"] == 1

def test_analis_3():
    stat = make_stat()
    ts = "2025-12-14T01:12:11+00:00"
    level = "ERROR"
    source = "a"
    mes = ""
    update_stat(make_dict(ts, level, source, mes), stat)
    ts = "2025-12-14T01:12:11+00:00"
    level = "ERROR"
    source = "b"
    mes = "привет"
    update_stat(make_dict(ts, level, source, mes), stat)
    assert top(stat) == [("a", 1), ("b", 1)]
    assert stat["total"] == 2

def test_analis_4():
    stat = make_stat()
    ts = "2024-12-14T01:12:11+00:00"
    level = "DEBUG"
    source = "SRC"
    mes = ""
    update_stat(make_dict(ts, level, source, mes), stat)
    ts = "2025-12-14T01:12:10+00:00"
    level = "INFO"
    source = "SRC"
    mes = "message"
    update_stat(make_dict(ts, level, source, mes), stat)
    assert stat["total"] == 2
    assert stat["st_source"]["SRC"] == {"total": 2, "error": 0}
    assert stat["st_level"]["ERROR"] == 0