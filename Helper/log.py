import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from os.path import exists, join
from os import makedirs
from .config import Config
from .logger_base import LoggerBase, ColoredFormatter


class Log(LoggerBase):
    # Rotating log files configuration
    LOG_SIZE = 16777216
    LOG_COUNT = 10

    @classmethod
    def Initialize(cls, app: Flask):
        config = Config()
        folder = config.Logging.Folder

        if not exists(folder): makedirs(folder)

        # Accept all messages on Flask logger, but display only up to the selected level
        app.logger.setLevel(logging.DEBUG)
        console_handler: logging.StreamHandler = app.logger.handlers[0]
        console_handler.setLevel(config.Logging.AppLevel)
        console_handler.setFormatter(ColoredFormatter('%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]'))

        # Attach new file handler
        file_handler = RotatingFileHandler(
            join(folder, 'scheduler.log'), maxBytes=cls.LOG_SIZE, backupCount=cls.LOG_COUNT)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]'))
        file_handler.setLevel(config.Logging.LogLevel)
        app.logger.addHandler(file_handler)

        super().Initialize(app.logger)
