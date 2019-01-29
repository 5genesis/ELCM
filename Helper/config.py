import yaml
from os.path import exists, abspath
from shutil import copy
from typing import Dict
import logging


class Logging:
    def __init__(self, data: Dict):
        self.data = data['Logging']

    @staticmethod
    def toLogLevel(level: str) -> int:
        if level.lower() == 'critical': return logging.CRITICAL
        if level.lower() == 'error': return logging.ERROR
        if level.lower() == 'warning': return logging.WARNING
        if level.lower() == 'info': return logging.INFO
        return logging.DEBUG

    @property
    def Folder(self):
        return abspath(self.data['Folder'])

    @property
    def AppLevel(self):
        return self.toLogLevel(self.data['AppLevel'])

    @property
    def LogLevel(self):
        return self.toLogLevel(self.data['LogLevel'])


class Config:
    FILENAME = 'config.yml'

    data = None

    def __init__(self):
        if self.data is None:
            self.Reload()

    def Reload(self):
        if not exists(self.FILENAME):
            copy('Helper/default_config', self.FILENAME)

        with open(self.FILENAME, 'r', encoding='utf-8') as file:
            self.data = yaml.safe_load(file)

    @property
    def Logging(self):
        return Logging(self.data)

    @property
    def Flask(self):
        return self.data['Flask']
