import yaml
from Helper import Level
from typing import List, Dict
from os.path import join
from ..action_information import ActionInformation


class Loader:
    @classmethod
    def EnsureFolder(cls, path: str) -> [(Level, str)]:
        from Helper import IO
        validation = []
        if not IO.EnsureFolder(path):
            validation.append((Level.INFO, f'Auto-generated folder: {path}'))
        return validation

    @classmethod
    def LoadFolder(cls, path: str, kind: str) -> [(Level, str)]:
        from Helper import IO
        ignored = []
        validation = []
        for file in IO.ListFiles(path):
            if file.endswith('.yml'):
                filePath = join(path, file)
                try:
                    validation.append((Level.INFO, f'Loading {kind}: {file}'))
                    data, v = cls.LoadFile(filePath)
                    validation.extend(v)
                    validation.extend(cls.ProcessData(data))
                except Exception as e:
                    validation.append((Level.ERROR, f"Exception loading {kind} file '{filePath}': {e}"))
            else:
                ignored.append(file)
        if len(ignored) != 0:
            validation.append((Level.WARNING,
                               f'Ignored the following files on the {kind}s folder: {(", ".join(ignored))}'))
        return validation

    @classmethod
    def LoadFile(cls, path: str) -> ((Dict | None), [(Level, str)]):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                raw = yaml.safe_load(file)
                return raw, []
        except Exception as e:
            return None, [(Level.ERROR, f"Unable to load file '{path}': {e}")]

    @classmethod
    def GetActionList(cls, data: List[Dict]) -> ([ActionInformation], [(Level, str)]):
        actionList = []
        validation = []

        for action in data:
            actionInfo = ActionInformation.FromMapping(action)
            if actionInfo is not None:
                actionList.append(actionInfo)
            else:
                validation.append((Level.ERROR, f'Action not correctly defined for element (data="{action}").'))
                actionList.append(ActionInformation.MessageAction(
                    'ERROR', f'Incorrect Action (data="{action}")'
                ))

        if len(actionList) == 0:
            validation.append((Level.WARNING, 'No actions defined'))
        else:
            for action in actionList:
                validation.append((Level.DEBUG, str(action)))

        return actionList, validation

    @classmethod
    def ProcessData(cls, data: Dict) -> [(Level, str)]:
        raise NotImplementedError

    @classmethod
    def Clear(cls):
        raise NotImplementedError
