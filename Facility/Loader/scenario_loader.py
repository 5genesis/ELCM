from Helper import Level
from .loader_base import Loader
from typing import Dict


class ScenarioLoader(Loader):
    scenarios: Dict[str, Dict] = {}

    @classmethod
    def ProcessData(cls, data: Dict) -> [(Level, str)]:
        validation = []
        keys = list(data.keys())

        if len(keys) > 1:
            validation.append((Level.WARNING, f'Multiple Scenarios defined on a single file: {keys}'))

        for key, value in data.items():
            if key in cls.scenarios.keys():
                validation.append((Level.WARNING, f'Redefining Scenario {key}'))
            cls.scenarios[key] = value
            validation.append((Level.DEBUG, f'{key}: {value}'))

        return validation

    @classmethod
    def Clear(cls):
        cls.scenarios = {}

    @classmethod
    def GetCurrentScenarios(cls):
        return cls.scenarios
