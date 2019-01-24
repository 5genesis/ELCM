import logging
from logging.handlers import RotatingFileHandler
from enum import Enum, unique
from flask import Flask
from os.path import exists, join
from os import makedirs
from .config import Config
import traceback


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


@unique
class Level(Enum):
    DEBUG, INFO, WARNING, ERROR, CRITICAL = range(5)


class Log:
    # Rotating log files configuration
    LOG_SIZE = 16777216
    LOG_COUNT = 10

    initialized = False
    app: Flask = None

    @classmethod
    def Initialize(cls, app: Flask):
        config = Config()
        folder = config.Logging.Folder

        if not exists(folder): makedirs(folder)

        # Accept all messages on Flask logger, but display only up to the selected level
        app.logger.setLevel(logging.DEBUG)
        console_handler: logging.StreamHandler = app.logger.handlers[0]
        console_handler.setLevel(config.Logging.AppLevel)

        # Attach new file handler
        file_handler = RotatingFileHandler(
            join(folder, 'scheduler.log'), maxBytes=cls.LOG_SIZE, backupCount=cls.LOG_COUNT)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]'))
        file_handler.setLevel(config.Logging.LogLevel)
        app.logger.addHandler(file_handler)

        cls.app = app
        cls.initialized = True

    @classmethod
    def D(cls, msg):
        if cls.initialized:
            cls.app.logger.debug(msg)
        else:
            print(f"[Log not initialized][DEBUG   ] {msg}")

    @classmethod
    def I(cls, msg):
        if cls.initialized:
            cls.app.logger.info(msg)
        else:
            print(f"[Log not initialized][INFO    ] {msg}")

    @classmethod
    def W(cls, msg):
        if cls.initialized:
            cls.app.logger.warning(msg)
        else:
            print(f"[Log not initialized][WARNING ] {msg}")

    @classmethod
    def E(cls, msg):
        if cls.initialized:
            cls.app.logger.error(msg)
        else:
            print(f"[Log not initialized][ERROR   ] {msg}")

    @classmethod
    def C(cls, msg):
        if cls.initialized:
            cls.app.logger.critical(msg)
        else:
            print(f"[Log not initialized][CRITICAL] {msg}")

    @staticmethod
    def State(condition: bool) -> str:
        return f'{"En" if condition else "Dis"}abled'

    @classmethod
    def Log(cls, level: Level, msg: str):
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
