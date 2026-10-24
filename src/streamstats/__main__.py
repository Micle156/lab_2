import argparse
import logging
import sys

from .analysis import update_stat
from .errors import StreamStatsError
from .parsers import (
    make_csv,
    make_else,
    make_jsonl,
)
from .report import build_report

# создание логгера для пакета с одним именем для всех модулей
log = logging.getLogger("streamstats")

# глобальный словарь статистики
stats = {
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

def reset_stats():
    """
    обновление словаря статистики, чтобы 
    между тестами статистика очищалась
    """
    global stats
    stats = {
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

def build_parser():
    """создание парсера, задание комманд"""
    parser = argparse.ArgumentParser(prog="streamstats")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("analyze", help = "анализ файлов и отчет")

    p.add_argument("INPUT", nargs="+", help="ввод 1 или более файлов")
    p.add_argument(
        "--format", nargs="+", required=True)

    p.add_argument("--output", help="путь к отчету")
    p.add_argument(
        "--skip-invalid", 
        action="store_true", 
        help="пропуск битых строк"
    )

    return parser

def process_csv(path, skip_invalid):
    """
    файл csv открывается и читается построчно
    вызывает функцию создание словаря события,
    обновления статистики
    возвращает:
    True - если успешно обработан файл
    false - если найдена ошибка
    """

    global stats
    
    with open(path, encoding="utf-8", newline = "") as f:
        line = f.readline()
        empty = True
        if line != "timestamp,level,source,message\r\n":
            empty = False

        for number, line in enumerate(f, start = 2):
            if not line.strip():
                continue
            try:
                event = make_csv(line, number)
            except StreamStatsError as e:
                if skip_invalid:
                    stats["skip"] += 1
                    log.warning("%s: %s", path, e)
                else:
                    log.error("%s: %s", path, e)
                    return False
            else:
                stats = update_stat(event, stats)
    if not empty and stats["total"] != 0:
        log.error("нет заголовка в csv")
        return False
    return True

def process_jsonl(path, skip_invalid):
    """
    файл jsonl открывается и читается построчно
    вызывает функцию создание словаря события,
    обновления статистики
    возвращает:
    True - если успешно обработан файл
    false - если найдена ошибка
    """

    global stats

    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, start = 1):
            if not line.strip():
                continue

            try:
                event = make_jsonl(line, number)
            except StreamStatsError as e:
                if skip_invalid:
                    stats["skip"] += 1
                    log.warning("%s: %s", path, e)
                else:
                    log.error("%s: %s", path, e)
                    return 2
            else:
                stats = update_stat(event, stats)

    return True



def main(argv = None):
    """
    вызов функции, строящей парсер
    проходит по аргументам,
    вызывает для каждого файла функцию
    обработки этого файла
    argv - для запуска из тестов
    возвращает для sys.exit() 2 или 0
    """

    parser = build_parser()
    args = parser.parse_args(argv)

    # уровень INFO показывает ERROR и CRITICAL
    # по умолчанию logging пишет в stderr
    # чтобы не смешиваться с полезным выводом
    logging.basicConfig(level=logging.INFO)

    reset_stats()

    if len(args.INPUT) != len(args.format):
        log.error("несоответствие форматов и файлов")
        return 2

    for ind in range(len(args.INPUT)):
        path = args.INPUT[ind]
        frmt = args.format[ind]
        if frmt == "csv":
            process = process_csv(path, args.skip_invalid)
        elif frmt == "jsonl":
            process = process_jsonl(path, args.skip_invalid)
        else:
            try:
                make_else(args.format)
            except StreamStatsError as e:
                log.error("%s", e)
                return 2
        
        if not process: # если False, то встречена ошибка
            return 2
                
    build_report(stats, args.output, args.skip_invalid)
    return 0

if __name__ == "__main__":
    sys.exit(main())