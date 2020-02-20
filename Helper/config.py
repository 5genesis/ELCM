import yaml
from os.path import exists, abspath, realpath, join
from os import getenv
from shutil import copy
from typing import Dict, List, Tuple, Optional
import logging
import platform
from REST import RestClient
from .log_level import Level


class validable:
    def __init__(self, data: Dict, section: str,
                 defaults: Dict[str, Tuple[Optional[object], "Level"]]):
        self.data = data
        self.section = section
        self.defaults = defaults

    def _keyOrDefault(self, key: str):
        if key in self.data.keys():
            return self.data[key]
        else:
            default = self.defaults.get(key, None)
            return default[0] if default is not None else None

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        res = []
        for key in self.defaults.keys():
            if key not in self.data:
                default, level = self.defaults[key]
                defaultText = f", using default '{default}'" if default is not None else ""
                res.append((level, f"'{key}' not defined under '{self.section}'{defaultText}"))
        if len(res) == 0:
            values = '; '.join([f'{key}: {self.data[key]}' for key in self.defaults.keys()])
            res.append((Level.INFO, f'{self.section} [{values}]'))
        return res


class restApi(validable):
    def __init__(self, data: Dict, section: str, defaults: Dict[str, Tuple[Optional[object], "Level"]]):
        if 'Host' not in defaults.keys(): defaults['Host'] = (None, Level.ERROR)
        if 'Port' not in defaults.keys(): defaults['Port'] = (None, Level.ERROR)
        super().__init__(data, section, defaults)

    @property
    def Host(self):
        return self._keyOrDefault('Host')

    @property
    def Port(self):
        return self._keyOrDefault('Port')

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        res = super().Validation
        if all([e[0] == Level.INFO for e in res]):
            # No errors, but check if a rest server can be created with the configuration
            try:
                _ = RestClient(self.Host, self.Port, "")
            except Exception as e:
                res.append((Level.ERROR, f'Exception creating {self.section} client: {e}'))
        return res


class Grafana(restApi):
    def __init__(self, data: Dict):
        defaults = {
            'Enabled': (False, Level.WARNING),
            'Bearer': ('', Level.WARNING),
            'ReportGenerator': ('', Level.WARNING)
        }
        super().__init__(data, "Grafana", defaults)

    @property
    def Enabled(self):
        return self._keyOrDefault('Enabled')

    @property
    def Bearer(self):
        return self._keyOrDefault('Bearer')

    @property
    def ReportGenerator(self):
        return self._keyOrDefault('ReportGenerator')

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        if not self.Enabled:
            return [(Level.INFO, "Grafana is disabled")]
        else:
            return super().Validation


class TapConfig(validable):
    def __init__(self, data: Dict):
        defaults = {
            'Enabled': (False, Level.WARNING),
            'OpenTap': (True, Level.WARNING),
            'Exe': ('tap.exe', Level.WARNING),
            'Folder': ('C:/Program Files/OpenTAP', Level.WARNING),
            'Results': ('C:/Program Files/OpenTAP/Results', Level.WARNING),
            'EnsureClosed': (False, Level.WARNING),
            'EnsureAdbClosed': (False, Level.WARNING),
        }
        super().__init__(data, 'Tap', defaults)

    @property
    def Enabled(self):
        return self._keyOrDefault('Enabled')

    @property
    def OpenTap(self):
        return self._keyOrDefault('OpenTap')

    @property
    def Exe(self):
        return self._keyOrDefault('Exe')

    @property
    def Folder(self):
        return self._keyOrDefault('Folder')

    @property
    def Results(self):
        return self._keyOrDefault('Results')

    @property
    def EnsureClosed(self):
        return self._keyOrDefault('EnsureClosed')

    @property
    def EnsureAdbClosed(self):
        return self._keyOrDefault('EnsureAdbClosed')

    @property
    def Path(self): return realpath(join(self.Folder, self.Exe))

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        if not self.Enabled:
            if 'Enabled' in self.data.keys():
                return [(Level.INFO, "TAP is disabled")]
            else:
                return [(Level.ERROR, "'Enabled' key not in 'Tap' configuration. Assuming Disabled.")]
        else:
            return super().Validation


class Dispatcher(restApi):
    def __init__(self, data: Dict):
        super().__init__(data, 'Dispatcher', {})


class SliceManager(restApi):
    def __init__(self, data: Dict):
        super().__init__(data, 'SliceManager', {})


class InfluxDb(restApi):
    def __init__(self, data: Dict):
        defaults = {
            'Enabled': (False, Level.WARNING),
            'User': (None, Level.ERROR),
            'Password': (None, Level.ERROR),
            'Database': (None, Level.ERROR),
        }
        super().__init__(data, 'InfluxDb', defaults)

    @property
    def Enabled(self):
        return self._keyOrDefault('Enabled')

    @property
    def User(self):
        return self._keyOrDefault('User')

    @property
    def Password(self):
        return self._keyOrDefault('Password')

    @property
    def Database(self):
        return self._keyOrDefault('Database')

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        if not self.Enabled:
            if 'Enabled' in self.data.keys():
                return [(Level.INFO, "InfluxDb is disabled")]
            else:
                return [(Level.ERROR, "'Enabled' key not in 'InfluxDb' configuration. Assuming Disabled.")]
        else:
            return super().Validation


class Logging(validable):
    def __init__(self, data: Dict):
        defaults = {
            'Folder': ('Logs', Level.WARNING),
            'AppLevel': ('info', Level.WARNING),
            'LogLevel': ('debug', Level.WARNING)
        }
        super().__init__(data, 'Logging', defaults)

    @staticmethod
    def toLogLevel(level: Optional[str]) -> int:
        if level is None or level.lower() == 'debug': return logging.DEBUG
        if level.lower() == 'info': return logging.INFO
        if level.lower() == 'warning': return logging.WARNING
        if level.lower() == 'error': return logging.ERROR
        return logging.CRITICAL

    @property
    def Folder(self):
        folder = self._keyOrDefault("Folder")
        return abspath(folder)

    @property
    def AppLevel(self):
        return self.toLogLevel(self._keyOrDefault("AppLevel"))

    @property
    def LogLevel(self):
        return self.toLogLevel(self._keyOrDefault("LogLevel"))


class Metadata(validable):
    def __init__(self, data: Dict):
        defaults = {
            "HostIp": ("127.0.0.1", Level.INFO),
            "Facility": ("", Level.INFO),
        }
        super().__init__(data, 'Metadata', defaults)

        self.HostName = platform.node()

    @property
    def HostIp(self): return self._keyOrDefault("HostIp")

    @property
    def Facility(self): return self._keyOrDefault("Facility")


class Config:
    FILENAME = 'config.yml'

    data = None
    Validation: List[Tuple['Level', str]] = []

    def __init__(self):
        if Config.data is None:
            self.Reload()

    def Reload(self):
        if not exists(Config.FILENAME):
            copy('Helper/default_config', Config.FILENAME)

        try:
            with open(Config.FILENAME, 'r', encoding='utf-8') as file:
                Config.data = yaml.safe_load(file)
        except Exception as e:
            from .log import Log
            Log.C(f"Exception while loading config file: {e}")
            return

        self.Validate()

    @property
    def Logging(self):
        return Logging(Config.data.get('Logging', {}))

    @property
    def Dispatcher(self):
        return Dispatcher(Config.data.get('Dispatcher', {}))

    @property
    def TempFolder(self):
        return Config.data.get('TempFolder', 'Temp')

    @property
    def Tap(self):
        return TapConfig(Config.data.get('Tap', {}))

    @property
    def Grafana(self):
        return Grafana(Config.data.get('Grafana', {}))

    @property
    def SliceManager(self):
        return SliceManager(Config.data.get('SliceManager', {}))

    @property
    def InfluxDb(self):
        return InfluxDb(Config.data.get('InfluxDb', {}))

    @property
    def Metadata(self):
        return Metadata(Config.data.get('Metadata', {}))

    def Validate(self):
        Config.Validation = []
        keys = set(Config.data.keys())
        keys.discard('Flask')
        keys.discard('TempFolder')

        if getenv('SECRET_KEY') is None:
            Config.Validation.append((Level.CRITICAL,
                                      "SECRET_KEY not defined. Use environment variables or set a value in .flaskenv"))

        if 'TempFolder' not in Config.data:
            Config.Validation.append((Level.INFO, "TempFolder not defined, using 'Temp'"))

        for entry in [self.Logging, self.Dispatcher, self.SliceManager, self.Tap,
                      self.Grafana, self.InfluxDb, self.Metadata, ]:
            Config.Validation.extend(entry.Validation)
            keys.discard(entry.section)

        if len(keys) != 0:
            Config.Validation.append((Level.WARNING, f"Unrecognized keys found: {(', '.join(keys))}"))
