from Helper import Level
from .loader_base import Loader
from ..action_information import ActionInformation
from ..dashboard_panel import DashboardPanel
from typing import Dict, List, Tuple


class TestCaseData:
    def __init__(self, data: Dict):
        # Shared keys
        self.AllKeys: List[str] = list(data.keys())
        self.Dashboard: (Dict | None) = data.pop('Dashboard', None)
        self.Standard: (bool | None) = data.pop('Standard', None)
        self.Custom: (List[str] | None) = data.pop('Custom', None)
        self.Distributed: bool = data.pop('Distributed', False)
        self.Parameters: Dict[str, Dict[str, str]] = data.pop('Parameters', {})

        # V2 only
        self.Name: (str | None) = data.pop('Name', None)
        self.Sequence: List[Dict] = data.pop('Sequence', [])


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
    def handleExperimentType(cls, defs: TestCaseData) -> [(Level, str)]:
        validation = []
        if defs.Standard is None:
            defs.Standard = (defs.Custom is None)
            validation.append((Level.WARNING, f'Standard not defined, assuming {defs.Standard}. Keys: {defs.AllKeys}'))
        return validation

    @classmethod
    def createDashboard(cls, key: str, defs: TestCaseData) -> [(Level, str)]:
        validation = []
        if defs.Dashboard is not None:
            cls.dashboards[key], validation = cls.getPanelList(defs.Dashboard)
        return validation

    @classmethod
    def createExtra(cls, key: str, defs: TestCaseData):
        cls.extra[key] = {
            'Standard': defs.Standard,
            'PublicCustom': (defs.Custom is not None and len(defs.Custom) == 0),
            'PrivateCustom': defs.Custom if defs.Custom is not None else [],
            'Parameters': defs.Parameters,
            'Distributed': defs.Distributed
        }

    @classmethod
    def validateParameters(cls, defs: TestCaseData) -> [(Level, str)]:
        validation = []
        for name, info in defs.Parameters.items():
            type, desc = (info['Type'], info['Description'])
            if name not in cls.parameters.keys():
                cls.parameters[name] = (type, desc)
            else:
                oldType, oldDesc = cls.parameters[name]
                if type != oldType or desc != oldDesc:
                    validation.append(
                        (Level.WARNING, f"Redefined parameter '{name}' with different settings: "
                                        f"'{oldType}' - '{type}'; '{oldDesc}' - '{desc}'. "
                                        f"Cannot guarantee consistency."))
        return validation

    @classmethod
    def ProcessData(cls, data: Dict) -> [(Level, str)]:
        version = str(data.pop('Version', 1))

        match version:
            case '1': return cls.processV1Data(data)
            case '2': return cls.processV2Data(data)
            case _: raise RuntimeError(f"Unknown testcase version '{version}'.")

    @classmethod
    def processV1Data(cls, data: Dict) -> [(Level, str)]:
        validation = []
        defs = TestCaseData(data)

        if defs.Dashboard is None:
            validation.append((Level.WARNING, f'Dashboard not defined. Keys: {defs.AllKeys}'))

        validation.extend(
            cls.handleExperimentType(defs))

        keys = list(data.keys())

        if len(keys) > 1:
            validation.append((Level.ERROR, f'Multiple TestCases defined on a single file: {list(keys)}'))

        for key in keys:
            cls.testCases[key], v = cls.GetActionList(data[key])
            validation.extend(v)

            cls.createExtra(key, defs)

            validation.extend(
                cls.createDashboard(key, defs))

            validation.extend(
                cls.validateParameters(defs))

        return validation

    @classmethod
    def processV2Data(cls, data: Dict) -> [(Level, str)]:
        validation = []
        defs = TestCaseData(data)

        validation.extend(
            cls.handleExperimentType(defs))

        cls.testCases[defs.Name], v = cls.GetActionList(defs.Sequence)
        validation.extend(v)

        cls.createExtra(defs.Name, defs)

        validation.extend(
            cls.createDashboard(defs.Name, defs))

        validation.extend(
            cls.validateParameters(defs))

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
