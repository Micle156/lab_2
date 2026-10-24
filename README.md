# Streamstats
Пакет `streamstats`, читающий события из CSV и JSONL и создающий статистический отчёт.

## Структура проекта

```
lab_02/
├── pyproject.toml
├── README.md
├── src/
│   └── streamstats/
│       ├── __init__.py
│       ├── __main__.py      # CLI
│       ├── errors.py        # исключения
│       ├── analysis.py      # анализ данных для отчета
│       ├── parsers.py       # валидация каждого запроса
│       └── report.py        # сборка и запись JSON
└── tests/
    ├── test_json_parser.py
    ├── test_csv_parser.py
    ├── test_analysis.py
    └── test_cli.py
```

## Функционал
- Читает CSV с заголовком и JSONL
- Считает:
  - общее число валидных событий (total)
  - по каждому уровню (by_level)
  - по каждому источнику: сколько всего и сколько ошибок (by_source)
  - топ 5 источников ошибок (top_error_sources)
  - первую и последнюю временную метку (first_timestamp и last_timestamp)
  - число пропущенных строк в режиме --skip-invalid (skipped)
- Обрабатывает несколько файлов за один запуск
- Поддерживает 2 режима

## Устновка
Нужен python 3.11+

```
pip install -e ".[dev]"
```

## Запуск

```text
python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output REPORT.json


python -m streamstats analyze INPUT --format jsonl --skip-invalid
```
если файлов несколько, нужно для каждого соответственно указать формат

### Примеры

Один CSV-файл:

```
python -m streamstats analyze events.csv --format csv --output report.json
```

Несколько файлов:

```
python -m streamstats analyze /a.csv /b.jsonl --format csv jsonl --output report.json
```

JSONL с пропуском битых строк:

```
python -m streamstats analyze events.jsonl --format jsonl --skip-invalid
```

### Команды проверки

```
python -m pytest
ruff check .
python -m streamstats --help
```

## Формат события

- timestamp - ISO 8601
- level : DEBUG / INFO / ERROR / CRITICAL
- source - непустая строка
- message - строка (может быть пустой)

### Пример CSV

```
timestamp,level,source,message
2026-10-06T10:00:00+00:00,INFO,api,Start
2026-10-06T10:01:00+00:00,ERROR,db,конец
```

### Пример JSONL

```
{"timestamp":"2026-10-06T10:00:00+00:00","level":"INFO","source":"api","message":"Start"}
{"timestamp":"2026-10-06T10:01:00+00:00","level":"ERROR","source":"db","message":""}
```

## Формат отчёта

```json
{
  "total": 12,
  "levels": {
    "DEBUG": 2,
    "INFO": 4,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 1
  },
  "sources": {
    "api": 4,
    "db": 4,
    "web": 4
  },
  "top_error_sources": [
    ["db", 2],
    ["api", 1],
    ["web", 1]
  ],
  "first_timestamp": "2026-10-06T10:00:00+00:00",
  "last_timestamp": "2026-10-06T10:10:00+00:00",
  "skipped": 0
}
```

- total — число валидных событий.
- levels — по каждому уровню.
- sources — по каждому источнику 
- top_error_sources — top-5 источников по числу ERROR/CRITICAL. При равных — по имени источника.
- first_timestamp / last_timestamp — границы по времени. null, если событий не было.
- skipped — число пропущенных строк (только при --skip-invalid).

### Отчет в режиме skip-invalid

отчёт в stderr с выводом ошибок в битых строках

### Отчет в обычном режиме

отчет в jsonl - файле

# Тестирование

```
python -m pytest                                       # все тесты
python -m pytest tests/test_cli.py               # конкретный файл
python -m pytest tests/test_analysis.py::test_1       # конкретный тест
python -m pytest tests/ -k "test_1"                    # по шаблону
python -m pytest -v                                    # подробный
```

## Линт и структура

```
ruff check .
```