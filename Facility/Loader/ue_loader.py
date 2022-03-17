from Helper import Level
from .loader_base import Loader
from ..action_information import ActionInformation
from typing import Dict, List


class UeLoader(Loader):
    ues: Dict[str, List[ActionInformation]] = {}

    @classmethod
    def ProcessFile(cls, path: str) -> [(Level, str)]:
        validation = []
        try:
            data, v = cls.LoadFile(path)
            validation.extend(v)
            keys = list(data.keys())

            if len(keys) > 1:
                validation.append((Level.WARNING, f'Multiple UEs defined on a single file: {keys}'))

            for key in keys:
                if key in cls.ues.keys():
                    validation.append((Level.WARNING, f'Redefining UE {key}'))
                actions, v = cls.GetActionList(data[key])
                validation.extend(v)
                cls.ues[key] = actions

        except Exception as e:
            validation.append((Level.ERROR, f'Exception loading UE file {path}: {e}'))

        return validation

    @classmethod
    def Clear(cls):
        cls.ues = {}

    @classmethod
    def GetCurrentUEs(cls):
        return cls.ues
