from os.path import exists
from shutil import copy
import yaml
from .action_information import ActionInformation
from Helper import Log
from typing import Dict, List


class Facility:
    FILENAME = 'facility.yml'
    data: Dict[str, Dict[str, List[ActionInformation]]] = None

    @classmethod
    def Reload(cls):
        def _parse(section: str, target: Dict):
            for identifier, actions in raw[section].items():
                actionList = []
                for action in actions:
                    actionInfo = ActionInformation.FromMapping(action)
                    if actionInfo is not None:
                        actionList.append(actionInfo)
                    else:
                        Log.W(f'Facility: Action not correctly defined for element {identifier}.')
                        actionList.append(ActionInformation.MessageAction(
                            'ERROR', f'Incorrect Action {identifier} (data="{action}")'
                        ))
                target[identifier] = actionList

        if not exists(cls.FILENAME):
            copy('Facility/default_facility', cls.FILENAME)

        with open(cls.FILENAME, 'r', encoding='utf-8') as file:
            raw = yaml.safe_load(file)
            testCases = {}
            ues = {}

            try:
                _parse('TestCases', testCases)
            except KeyError:
                Log.W('Facility: No TestCases key defined in facility.yml')

            try:
                _parse('UEs', ues)
            except KeyError:
                Log.W('Facility: No UEs key defined in facility.yml')

            cls.data = {'TestCases': testCases, 'UEs': ues}


    @classmethod
    def GetUEActions(cls, id: str) -> List[ActionInformation]:
        return cls.getFromSection('UEs', id)

    @classmethod
    def GetTestCaseActions(cls, id: str) -> List[ActionInformation]:
        return cls.getFromSection('TestCases', id)

    @classmethod
    def getFromSection(cls, section: str, id: str) -> List[ActionInformation]:
        if cls.data is None: cls.Reload()

        if id in cls.data[section].keys():
            return cls.data[section][id]
        return []
