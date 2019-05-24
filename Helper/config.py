import yaml
from os.path import exists, abspath
from shutil import copy
from typing import Dict
import logging
from os.path import realpath, join


class Grafana:
    def __init__(self, data: Dict):
        self.data = data

        self.Enabled = data['Enabled']
        self.Host = data['Host']
        self.Port = data['Port']
        self.Bearer = data['Bearer']


class TapConfig:
    def __init__(self, data: Dict):
        self.data = data

        self.Exe = data['Exe']
        self.Folder = data['Folder']
        self.Results = data['Results']
        self.EnsureClosed = data['EnsureClosed']

    @property
    def Path(self): return realpath(join(self.Folder, self.Exe))


class Dispatcher:
    def __init__(self, data: Dict):
        self.data = data['Dispatcher']

    @property
    def Host(self):
        return self.data['Host']

    @property
    def Port(self):
        return self.data['Port']


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
    def Dispatcher(self):
        return Dispatcher(self.data)

    @property
    def Flask(self):
        return self.data['Flask']

    @property
    def TempFolder(self):
        return self.data['TempFolder']

    @property
    def Tap(self):
        return TapConfig(self.data['Tap'])

    @property
    def Grafana(self):
        return Grafana(self.data['Grafana'])
