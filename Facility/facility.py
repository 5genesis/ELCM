from os.path import exists
from shutil import copy
import yaml
from .action_information import ActionInformation
from .dashboard_panel import DashboardPanel
from Helper import Log
from typing import Dict, List, Union


class Facility:
    FILENAME = 'facility.yml'
    data: Dict[str, Dict[str, List[ActionInformation]]] = None

    @classmethod
    def Reload(cls):
        def _parse_ActionInformation(section: str, target: Dict):
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

        def _parse_DashboardPanel(section: str, target: Dict):
            for identifier, dashboard in raw[section].items():
                panelList = []
                for panel in dashboard:
                    try:
                        parsedPanel = DashboardPanel(panel)
                        panelList.append(parsedPanel)
                    except:
                        Log.W(f"Unable to parse Dashboard Panel for id: {identifier}. Ignored")
                target[identifier] = panelList

        if not exists(cls.FILENAME):
            copy('Facility/default_facility', cls.FILENAME)

        with open(cls.FILENAME, 'r', encoding='utf-8') as file:
            raw = yaml.safe_load(file)
            testCases = {}
            ues = {}
            dashboards = {}

            try:
                _parse_ActionInformation('TestCases', testCases)
            except KeyError:
                Log.W('Facility: No TestCases key defined in facility.yml')

            try:
                _parse_ActionInformation('UEs', ues)
            except KeyError:
                Log.W('Facility: No UEs key defined in facility.yml')

            try:  # TODO: CLEANUP
                _parse_DashboardPanel('Dashboards', dashboards)
            except KeyError:
                Log.W('Facility: No Dashboards key defined in facility.yml')

            cls.data = {'TestCases': testCases, 'UEs': ues, 'Dashboards': dashboards}


    @classmethod
    def GetUEActions(cls, id: str) -> List[ActionInformation]:
        return cls.getFromSection('UEs', id)

    @classmethod
    def GetTestCaseActions(cls, id: str) -> List[ActionInformation]:
        return cls.getFromSection('TestCases', id)

    @classmethod
    def GetTestCaseDashboards(cls, id: str) -> List[DashboardPanel]:
        res = cls.getFromSection('Dashboards', id)
        return res

    @classmethod
    def getFromSection(cls, section: str, id: str) -> List[Union[ActionInformation, DashboardPanel]]:
        if cls.data is None: cls.Reload()

        if id in cls.data[section].keys():
            return cls.data[section][id]
        return []
