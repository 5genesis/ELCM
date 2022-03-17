from Helper import Level
from .loader_base import Loader
from ..action_information import ActionInformation
from ..dashboard_panel import DashboardPanel
from typing import Dict, List, Tuple


class TestCaseLoader(Loader):
    testCases: Dict[str, List[ActionInformation]] = {}
    extra: Dict[str, Dict[str, object]] = {}
    dashboards: Dict[str, List[DashboardPanel]] = {}
    parameters: Dict[str, Tuple[str, str]] = {}  # For use only while processing data, not necessary afterwards

    @classmethod
    def getPanelList(cls, data: Dict) -> ([DashboardPanel], [(Level, str)]):
        validation = []
        panelList = []
        for panel in data:
            try:
                parsedPanel = DashboardPanel(panel)
                valid, error = parsedPanel.Validate()
                if not valid:
                    validation.append((Level.ERROR, f'Could not validate panel (data={panel}) - {error}'))
                else:
                    panelList.append(parsedPanel)
            except Exception as e:
                validation.append((Level.ERROR, f"Unable to parse Dashboard Panel (data={panel}), ignored. {e}"))

        validation.append((Level.DEBUG, f'Defined {len(panelList)} dashboard panels'))
        return panelList, validation

    @classmethod
    def ProcessData(cls, data: Dict) -> [(Level, str)]:
        validation = []

        allKeys = list(data.keys())
        dashboard = data.pop('Dashboard', None)
        standard = data.pop('Standard', None)
        custom = data.pop('Custom', None)
        distributed = data.pop('Distributed', False)
        parameters = data.pop('Parameters', {})

        if dashboard is None:
            validation.append((Level.WARNING, f'Dashboard not defined. Keys: {allKeys}'))

        if standard is None:
            standard = (custom is None)
            validation.append((Level.WARNING,
                               f'Standard not defined, assuming {standard}. Keys: {allKeys}'))
        keys = list(data.keys())

        if len(keys) > 1:
            validation.append((Level.ERROR, f'Multiple TestCases defined on a single file: {list(keys)}'))
        for key in keys:
            cls.testCases[key], v = cls.GetActionList(data[key])
            validation.extend(v)

            cls.extra[key] = {
                'Standard': standard,
                'PublicCustom': (custom is not None and len(custom) == 0),
                'PrivateCustom': custom if custom is not None else [],
                'Parameters': parameters,
                'Distributed': distributed
            }

            if dashboard is not None:
                cls.dashboards[key], v = cls.getPanelList(dashboard)
                validation.extend(v)

        for name, info in parameters.items():
            type, desc = (info['Type'], info['Description'])
            if name not in parameters.keys():
                parameters[name] = (type, desc)
            else:
                oldType, oldDesc = parameters[name]
                if type != oldType or desc != oldDesc:
                    validation.append(
                        (Level.WARNING, f"Redefined parameter '{name}' with different settings: "
                                        f"'{oldType}' - '{type}'; '{oldDesc}' - '{desc}'. "
                                        f"Cannot guarantee consistency."))

        return validation

    @classmethod
    def Clear(cls):
        cls.testCases = {}
        cls.extra = {}
        cls.dashboards = {}
        cls.parameters = {}

    @classmethod
    def GetCurrentTestCases(cls):
        return cls.testCases

    @classmethod
    def GetCurrentTestCaseExtras(cls):
        return cls.extra

    @classmethod
    def GetCurrentDashboards(cls):
        return cls.dashboards
