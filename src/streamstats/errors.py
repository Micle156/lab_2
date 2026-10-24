class StreamStatsError(Exception):
    """базовое исключение пакета"""


class UnSupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат"""


class UncorrectedEventsError(StreamStatsError):
    """Некорректное событие"""


class UncorrectTimeError(StreamStatsError):
    """Неверная временная метка"""


class CliConfigError(StreamStatsError):
    """Ошибка конфигурации CLI"""