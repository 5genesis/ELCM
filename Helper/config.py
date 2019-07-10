import yaml
from os.path import exists, abspath
from shutil import copy
from typing import Dict
import logging
from os.path import realpath, join


class restApi:
    def __init__(self, data: Dict):
        self.data = data

        self.Host = data.get('Host', '')
        self.Port = data.get('Port', '')


class Grafana(restApi):
    def __init__(self, data: Dict):
        super().__init__(data)

        self.Enabled = data.get('Enabled', False)
        self.Bearer = data.get('Bearer', '')
        self.ReportGenerator = data.get('ReportGenerator', '')


class TapConfig:
    def __init__(self, data: Dict):
        self.data = data

        self.Exe = data.get('Exe', '')
        self.Folder = data.get('Folder', '')
        self.Results = data.get('Results', '')
        self.EnsureClosed = data.get('EnsureClosed', False)

    @property
    def Path(self): return realpath(join(self.Folder, self.Exe))


class Dispatcher(restApi): pass


class SliceManager(restApi): pass


class InfluxDb(restApi):
    def __init__(self, data: Dict):
        super().__init__(data)

        self.User = data.get("User", "")
        self.Password = data.get("Password", "")
        self.Database = data.get("Database", "")


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
        return Dispatcher(self.data.get('Dispatcher', {}))

    @property
    def Flask(self):
        return self.data['Flask']

    @property
    def TempFolder(self):
        return self.data['TempFolder']

    @property
    def Tap(self):
        return TapConfig(self.data.get('Tap', {}))

    @property
    def Grafana(self):
        return Grafana(self.data.get('Grafana', {}))

    @property
    def SliceManager(self):
        return SliceManager(self.data.get('SliceManager', {}))

    @property
    def InfluxDb(self):
        return InfluxDb(self.data.get('InfluxDb', {}))
