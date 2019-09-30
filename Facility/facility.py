from os.path import exists, abspath, join
from os import makedirs, listdir
from shutil import copy
import yaml
from .action_information import ActionInformation
from .dashboard_panel import DashboardPanel
from Helper import Log, Level
from typing import Dict, List, Union, Tuple, Callable, Optional


class Facility:
    TESTCASE_FOLDER = abspath('TestCases')
    UE_FOLDER = abspath('UEs')
    data: Dict[str, Dict[str, List[ActionInformation]]] = None
    Validation: List[Tuple[Level, str]] = []

    @classmethod
    def Reload(cls):
        def _ensureFolder(path: str):
            if not exists(path):
                makedirs(path)
                cls.Validation.append((Level.INFO, f'Auto-generated folder: {path}'))

        def _loadFolder(path: str, kind: str, callable: Callable):
            ignored = []
            for file in [f for f in listdir(path)]:
                if file.endswith('.yml'):
                    cls.Validation.append((Level.INFO, f'Loading {kind}: {file}'))
                    callable(join(path, file))
                else:
                    ignored.append(file)
            if len(ignored) != 0:
                cls.Validation.append((Level.WARNING,
                                       f'Ignored the following files on the {kind}s folder: {(", ".join(ignored))}'))

        def _loadFile(path: str) -> Optional[Dict]:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    raw = yaml.safe_load(file)
                    return raw
            except Exception as e:
                cls.Validation.append((Level.ERROR, f"Unable to load file '{path}': {e}"))
                return None

        def _get_ActionList(data: Dict) -> List[ActionInformation]:
            actionList = []
            for action in data:
                actionInfo = ActionInformation.FromMapping(action)
                if actionInfo is not None:
                    actionList.append(actionInfo)
                else:
                    cls.Validation.append((Level.ERROR, f'Action not correctly defined for element (data="{action}").'))
                    actionList.append(ActionInformation.MessageAction(
                        'ERROR', f'Incorrect Action (data="{action}")'
                    ))
            if len(actionList) == 0:
                cls.Validation.append((Level.WARNING, 'No actions defined'))
            else:
                for action in actionList:
                    cls.Validation.append((Level.DEBUG, str(action)))
            return actionList

        def _get_PanelList(data: Dict) -> List[DashboardPanel]:
            panelList = []
            for panel in data:
                try:
                    parsedPanel = DashboardPanel(panel)
                    valid, error = parsedPanel.Validate()
                    if not valid:
                        cls.Validation.append((Level.ERROR, f'Could not validate panel (data={panel}) - {error}'))
                    else:
                        panelList.append(parsedPanel)
                except Exception as e:
                    cls.Validation.append((Level.ERROR, f"Unable to parse Dashboard Panel (data={panel}), ignored. {e}"))
            cls.Validation.append((Level.DEBUG, f'Defined {len(panelList)} dashboard panels'))
            return panelList

        def _testcaseLoader(path: str):
            try:
                data = _loadFile(path)

                keys = list(data.keys())
                dashboard = data.get('Dashboard', None)

                if dashboard is not None:
                    keys.remove('Dashboard')
                else:
                    cls.Validation.append((Level.WARNING, f'Dashboard not defined. Keys: {list(keys)}'))

                if len(keys) > 1:
                    cls.Validation.append((Level.ERROR, f'Multiple TestCases defined on a single file: {list(keys)}'))
                for key in keys:
                    testCases[key] = _get_ActionList(data[key])
                    if dashboard is not None:
                        dashboards[key] = _get_PanelList(dashboard)
            except Exception as e:
                cls.Validation.append((Level.ERROR, f'Exception loading TestCase file {path}: {e}'))

        def _ueLoader(path: str):
            try:
                data = _loadFile(path)
                keys = data.keys()
                if len(keys) > 1:
                    cls.Validation.append((Level.WARNING, f'Multiple UEs defined on a single file: {list(keys)}'))
                for key in keys:
                    actions = _get_ActionList(data[key])
                    ues[key] = actions
            except Exception as e:
                cls.Validation.append((Level.ERROR, f'Exception loading UE file {path}: {e}'))

        cls.Validation.clear()

        _ensureFolder(cls.TESTCASE_FOLDER)
        _ensureFolder(cls.UE_FOLDER)

        testCases = {}
        ues = {}
        dashboards = {}

        _loadFolder(cls.TESTCASE_FOLDER, "TestCase", _testcaseLoader)
        _loadFolder(cls.UE_FOLDER, "UE", _ueLoader)

        for collection, name in [(testCases, "TestCases"), (ues, "UEs"), (dashboards, "DashBoards")]:
            keys = collection.keys()
            if len(keys) == 0:
                cls.Validation.append((Level.WARNING, f'No {name} defined on the facility.'))
            else:
                cls.Validation.append((Level.INFO, f'{len(keys)} {name} defined on the facility: {(", ".join(keys))}.'))

        cls.data = {'UEs': ues, 'TestCases': testCases, 'Dashboards': dashboards}

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
