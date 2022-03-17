from Helper import Level
from .loader_base import Loader
from typing import Dict


class ScenarioLoader(Loader):
    scenarios: Dict[str, Dict] = {}

    @classmethod
    def ProcessFile(cls, path: str) -> [(Level, str)]:
        validation = []
        try:
            data, v = cls.LoadFile(path)
            validation.extend(v)
            keys = list(data.keys())

            if len(keys) > 1:
                validation.append((Level.WARNING, f'Multiple Scenarios defined on a single file: {keys}'))

            for key, value in data.items():
                if key in cls.scenarios.keys():
                    validation.append((Level.WARNING, f'Redefining Scenario {key}'))
                cls.scenarios[key] = value
                validation.append((Level.DEBUG, f'{key}: {value}'))

        except Exception as e:
            validation.append((Level.ERROR, f'Exception loading Resource file {path}: {e}'))
        return validation

    @classmethod
    def Clear(cls):
        cls.scenarios = {}

    @classmethod
    def GetCurrentScenarios(cls):
        return cls.scenarios
