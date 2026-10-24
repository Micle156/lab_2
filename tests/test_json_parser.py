import json
from datetime import UTC, datetime

import pytest

from streamstats.errors import UncorrectedEventsError, UncorrectTimeError
from streamstats.parsers import make_jsonl

"""корректные тесты"""

def test_json_1():
    f = json.dumps({
        "timestamp": "2005-10-05T10:01:56+00:00",
        "level": "INFO",
        "source": "api",
        "message": "MES"
    })
    number = 1
    event = make_jsonl(f, number)

    assert event["timestamp"] == datetime(
        2005, 10, 5, 10, 
        1, 56, 
        tzinfo=UTC
    )
    assert event["level"] == "INFO"
    assert event["source"] == "api"
    assert event["message"] == "MES"

def test_json_2():
    f = json.dumps({
        "timestamp": "2005-10-05T10:01:56+00:00",
        "level": "ERROR",
        "source": "api",
        "message": ""
    })
    number = 1
    event = make_jsonl(f, number)

    assert event["timestamp"] == datetime(
        2005, 10, 5, 10, 
        1, 56, 
        tzinfo=UTC
    )
    assert event["level"] == "ERROR"
    assert event["source"] == "api"
    assert event["message"] == ""

def test_json_3():
    f = json.dumps({
        "timestamp": "2005-10-05T10:01:56+00:00",
        "level": "ERROR",
        "source": "источник",
        "message": "привет"
    })
    number = 1
    event = make_jsonl(f, number)

    assert event["timestamp"] == datetime(
        2005, 10, 5, 10, 
        1, 56, 
        tzinfo=UTC
    )
    assert event["level"] == "ERROR"
    assert event["source"] == "источник"
    assert event["message"] == "привет"

"""некорректные тесты"""

def test_json_4():
    with pytest.raises(UncorrectedEventsError):
        f = json.dumps({
            "timestamp": "2005-10-05T10:01:56+00:00",
            "level": "ERROR",
            "source": "api",
            "message": "",
            "next": ""
        })
        number = 1
        make_jsonl(f, number)

def test_json_5():
    with pytest.raises(UncorrectedEventsError):
        f = '{"timestamp":"2005-10-05T10:01:56+00:00",'
        '"level":"ERROR","source":"api","message":""'
        number = 1
        make_jsonl(f, number)

def test_json_6():
    with pytest.raises(UncorrectedEventsError):
        f = 'not json'
        number = 1
        make_jsonl(f, number)

def test_json_7():
    with pytest.raises(UncorrectedEventsError):
        f = "[1, 2, 3]"
        number = 1
        make_jsonl(f, number)

def test_json_8():
    with pytest.raises(UncorrectTimeError):
        f = json.dumps({
            "timestamp": "",
            "level": "ERROR",
            "source": "api",
            "message": ""
        })
        number = 1
        make_jsonl(f, number)

def test_json_9():
    with pytest.raises(UncorrectTimeError):
        f = json.dumps({
            "timestamp": "2006-23-2T01:01:01+00:00",
            "level": "ERROR",
            "source": "api",
            "message": ""
        })
        number = 1
        make_jsonl(f, number)

def test_json_10():
    with pytest.raises(UncorrectedEventsError):
        f = '{"timestamp":"2006-23-2T01:01:01+00:00",'
        '"level":"ERROR","source":"api"}'
        number = 1
        make_jsonl(f, number)

def test_json_11():
    with pytest.raises(UncorrectedEventsError):
        f = '{"timestamp":"2006-23-2T01:01:01+00:00",'
        '"level":"ERROR","message":"привет"'
        number = 1
        make_jsonl(f, number)