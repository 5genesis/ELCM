import logging
from enum import Enum, unique
import traceback
from typing import Union


@unique
class Level(Enum):
    DEBUG, INFO, WARNING, ERROR, CRITICAL = range(5)


class ColoredFormatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    RESET_SEQ = '\033[0m'
    COLOR_SEQ = '\033[1;%dm'

    COLORS = {
        'WARNING': YELLOW,
        'INFO': WHITE,
        'DEBUG': BLUE,
        'ERROR': RED,
        'CRITICAL': MAGENTA
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            color_levelname = self.COLOR_SEQ \
                              % (30 + self.COLORS[record.levelname]) \
                              + record.levelname \
                              + self.RESET_SEQ
            record.levelname = color_levelname
        return logging.Formatter.format(self, record)


class LoggerBase:
    _logger = None
    _initialized = False

    @classmethod
    def Initialize(cls, logger):
        cls._logger = logger
        cls._initialized = True

    @classmethod
    def _dump(cls, level: str, msg: str):
        if cls._initialized:
            method = getattr(cls._logger, level.lower())
            method(msg)
        else:
            print(f"[Log not initialized][{level}] {msg}")

    @classmethod
    def D(cls, msg): cls._dump('DEBUG', msg)

    @classmethod
    def I(cls, msg): cls._dump('INFO', msg)

    @classmethod
    def W(cls, msg): cls._dump('WARNING', msg)

    @classmethod
    def E(cls, msg): cls._dump('ERROR', msg)

    @classmethod
    def C(cls, msg): cls._dump('CRITICAL', msg)

    @staticmethod
    def State(condition: bool) -> str:
        return f'{"En" if condition else "Dis"}abled'

    @classmethod
    def Log(cls, level: Union[Level, str], msg: str):
        if isinstance(level, str):
            level = Level[level]

        if level == Level.DEBUG: cls.D(msg)
        if level == Level.INFO: cls.I(msg)
        if level == Level.WARNING: cls.W(msg)
        if level == Level.ERROR: cls.E(msg)
        if level == Level.CRITICAL: cls.C(msg)

    @classmethod
    def Traceback(cls, info):
        exc_type, exc_value, exc_traceback = info
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=2)
        for line in lines:
            cls.D(line.strip())
