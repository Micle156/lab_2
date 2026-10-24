import csv
import io
import json
from datetime import datetime

from .errors import UncorrectedEventsError, UncorrectTimeError, UnSupportedFormatError

HEAD_SCV = "timestamp,level,source,message\n"


def make_csv(line, number):
    line = line.strip()

    if not line:
        raise UncorrectedEventsError(
            f"line {number} - пустая строка"
        )

    raw = next(csv.DictReader(io.StringIO(HEAD_SCV + line)), None)
    # берет заголовок со строкой как файл и подает в функцию

    if raw is None:
        raise UncorrectedEventsError(
            f"line {number} - некорректный csv"
        )

    if None in raw:
        raise UncorrectedEventsError(
            "лишние поля в событии/не достает полей в событии"
        )
    
    return raw_valid(raw, number)

def make_jsonl(line, number):
    line = line.strip()

    if not line:
        raise UncorrectedEventsError(
            f"line {number} - пустая строка"
        )

    try:
        raw = json.loads(line) # собирает словарь события
    except json.JSONDecodeError:
        raise UncorrectedEventsError(
            f"line {number} - некорректный jsonl"
        )

    if not isinstance(raw, dict):
        raise UncorrectedEventsError(
            f"line {number} - некорректный jsonl"
        )

    if len(raw) != 4:
        raise UncorrectedEventsError(
            "лишние поля в событии/не достает полей в событии"
        )
    
    return raw_valid(raw, number)

def make_else(frmt):
    raise UnSupportedFormatError(f"неизвестный формат {frmt}")

def raw_valid(raw, number):
    """
    проверяет словарь события на корректность полей,
    переводит timestamp в datetime
    чтобы можно было сравнивать дату и время 
    """

    ts = raw.get("timestamp")
    level = raw.get("level")
    source = raw.get("source")
    mes = raw.get("message")

    if not isinstance(ts, str) or not ts:
        raise UncorrectTimeError(
            f"line {number} - некорректный timestammp"
        )

    try:
        timestamp = datetime.fromisoformat(ts)
    except ValueError:
        raise UncorrectTimeError(
            f"line {number} - неверный timestamp"
        )

    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise UncorrectedEventsError(
            f"line {number} - некорректный level"
        )

    if not isinstance(source, str) or not source:
        raise UncorrectedEventsError(
            f"line {number} - некорректный source"
            )
    
    if not isinstance(mes, str):
            raise UncorrectedEventsError(
                f"line {number} - некорректный message"
            )

    return {
        "timestamp": timestamp,
        "level": level,
        "source": source,
        "message": mes
    } 