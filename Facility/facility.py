from os.path import abspath, join
import yaml
from .action_information import ActionInformation
from .dashboard_panel import DashboardPanel
from .resource import Resource
from Helper import Log, Level
from typing import Dict, List, Tuple, Callable, Optional
from threading import Lock
from Utils import synchronized


class Facility:
    lock = Lock()
    requesters: Dict[str, List[str]] = {}
    activeExperiments = 0
    activeExclusive: Optional[int] = None

    TESTCASE_FOLDER = abspath('TestCases')
    UE_FOLDER = abspath('UEs')
    RESOURCE_FOLDER = abspath('Resources')
    SCENARIO_FOLDER = abspath('Scenarios')

    ues: Dict[str, List[ActionInformation]] = {}
    testCases: Dict[str, List[ActionInformation]] = {}
    extra: Dict[str, Dict[str, object]] = {}
    dashboards: Dict[str, List[ActionInformation]] = {}
    resources: Dict[str, Resource] = {}
    scenarios: Dict[str, Dict] = {}

    Validation: List[Tuple[Level, str]] = []

    @classmethod
    def Reload(cls):
        from Helper import IO
        allParameters: Dict[str, Tuple[str, str]] = {}

        def _ensureFolder(path: str):
            if not IO.EnsureFolder(path):
                cls.Validation.append((Level.INFO, f'Auto-generated folder: {path}'))

        def _loadFolder(path: str, kind: str, callable: Callable):
            ignored = []
            for file in IO.ListFiles(path):
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
                    cls.Validation.append((Level.ERROR,
                                           f"Unable to parse Dashboard Panel (data={panel}), ignored. {e}"))
            cls.Validation.append((Level.DEBUG, f'Defined {len(panelList)} dashboard panels'))
            return panelList

        def _testcaseLoader(path: str):
            try:
                data = _loadFile(path)

                allKeys = list(data.keys())
                dashboard = data.pop('Dashboard', None)
                standard = data.pop('Standard', None)
                custom = data.pop('Custom', None)
                distributed = data.pop('Distributed', False)
                parameters = data.pop('Parameters', {})

                if dashboard is None:
                    cls.Validation.append((Level.WARNING, f'Dashboard not defined. Keys: {allKeys}'))

                if standard is None:
                    standard = (custom is None)
                    cls.Validation.append((Level.WARNING,
                                           f'Standard not defined, assuming {standard}. Keys: {allKeys}'))
                keys = list(data.keys())

                if len(keys) > 1:
                    cls.Validation.append((Level.ERROR, f'Multiple TestCases defined on a single file: {list(keys)}'))
                for key in keys:
                    testCases[key] = _get_ActionList(data[key])

                    extra[key] = {
                        'Standard': standard,
                        'PublicCustom': (custom is not None and len(custom) == 0),
                        'PrivateCustom': custom if custom is not None else [],
                        'Parameters': parameters,
                        'Distributed': distributed
                    }

                    if dashboard is not None:
                        dashboards[key] = _get_PanelList(dashboard)

                for name, info in parameters.items():
                    type, desc = (info['Type'], info['Description'])
                    if name not in allParameters.keys():
                        allParameters[name] = (type, desc)
                    else:
                        oldType, oldDesc = allParameters[name]
                        if type != oldType or desc != oldDesc:
                            cls.Validation.append(
                                (Level.WARNING, f"Redefined parameter '{name}' with different settings: "
                                                f"'{oldType}' - '{type}'; '{oldDesc}' - '{desc}'. "
                                                f"Cannot guarantee consistency."))
            except Exception as e:
                cls.Validation.append((Level.ERROR, f'Exception loading TestCase file {path}: {e}'))

        def _ueLoader(path: str):
            try:
                data = _loadFile(path)
                keys = data.keys()
                if len(keys) > 1:
                    cls.Validation.append((Level.WARNING, f'Multiple UEs defined on a single file: {list(keys)}'))
                for key in keys:
                    if key in ues.keys():
                        cls.Validation.append((Level.WARNING, f'Redefining UE {key}'))
                    actions = _get_ActionList(data[key])
                    ues[key] = actions
            except Exception as e:
                cls.Validation.append((Level.ERROR, f'Exception loading UE file {path}: {e}'))

        def _resourceLoader(path: str):
            try:
                data = _loadFile(path)
                resource = Resource(data)
                if resource.Id in resources.keys():
                    cls.Validation.append((Level.WARNING, f'Redefining Resource {resource.Id}'))
                resources[resource.Id] = resource
            except Exception as e:
                cls.Validation.append((Level.ERROR, f'Exception loading Resource file {path}: {e}'))

        def _scenarioLoader(path: str):
            try:
                data = _loadFile(path)
                if len(data.keys()) > 1:
                    cls.Validation.append((Level.WARNING, f'Multiple Scenarios defined on a single file: {list(keys)}'))
                for key, value in data.items():
                    if key in scenarios.keys():
                        cls.Validation.append((Level.WARNING, f'Redefining Scenario {key}'))
                    scenarios[key] = value
                    cls.Validation.append((Level.DEBUG, f'{key}: {value}'))
            except Exception as e:
                cls.Validation.append((Level.ERROR, f'Exception loading Resource file {path}: {e}'))

        cls.Validation.clear()

        # Generate all folders
        for folder in [cls.TESTCASE_FOLDER, cls.UE_FOLDER, cls.RESOURCE_FOLDER, cls.SCENARIO_FOLDER]:
            _ensureFolder(folder)

        testCases = {}
        ues = {}
        dashboards = {}
        extra = {}
        scenarios = {}

        if len(cls.BusyResources()) != 0:
            resources = cls.resources
            cls.Validation.append((Level.WARNING, "Resources in use, skipping reload"))
        else:
            resources = {}
            _loadFolder(cls.RESOURCE_FOLDER, "Resource", _resourceLoader)

        _loadFolder(cls.TESTCASE_FOLDER, "TestCase", _testcaseLoader)
        _loadFolder(cls.UE_FOLDER, "UE", _ueLoader)
        _loadFolder(cls.SCENARIO_FOLDER, "Scenario", _scenarioLoader)

        for collection, name in [(testCases, "TestCases"), (ues, "UEs"),
                                 (dashboards, "DashBoards"), (resources, "Resources"),
                                 (scenarios, "Scenarios")]:
            keys = collection.keys()
            if len(keys) == 0:
                cls.Validation.append((Level.WARNING, f'No {name} defined on the facility.'))
            else:
                cls.Validation.append((Level.INFO, f'{len(keys)} {name} defined on the facility: {(", ".join(keys))}.'))

        cls.ues = ues
        cls.testCases = testCases
        cls.extra = extra
        cls.dashboards = dashboards
        cls.resources = resources
        cls.scenarios = scenarios

    @classmethod
    def GetUEActions(cls, id: str) -> List[ActionInformation]:
        return cls.ues.get(id, [])

    @classmethod
    def GetTestCaseActions(cls, id: str) -> List[ActionInformation]:
        return cls.testCases.get(id, [])

    @classmethod
    def GetMonroeActions(cls) -> List[ActionInformation]:
        return cls.testCases.get("MONROE_Base", [])

    @classmethod
    def GetTestCaseDashboards(cls, id: str) -> List[DashboardPanel]:
        return cls.dashboards.get(id, [])

    @classmethod
    def GetTestCaseExtra(cls, id: str) -> Dict[str, object]:
        return cls.extra.get(id, {})

    @classmethod
    def BusyResources(cls) -> List[Resource]:
        return [res for res in cls.resources.values() if res.Locked]

    @classmethod
    def IdleResources(cls) -> List[Resource]:
        return [res for res in cls.resources.values() if not res.Locked]

    @classmethod
    def Resources(cls):
        return cls.resources

    @classmethod
    def Scenarios(cls):
        return cls.scenarios

    @classmethod
    @synchronized(lock)
    def TryLockResources(cls, ids: List[str], owner: 'ExecutorBase', exclusive: bool) -> bool:
        executor = owner.ExecutionId
        resources: List[Resource] = list(filter(None, [cls.resources.get(id, None) for id in ids]))
        resourceIds = [resource.Id for resource in resources]
        lockedResources: List[str] = []

        if owner.ExecutionId not in cls.requesters.keys():
            cls.requesters[executor] = resourceIds

        # For exclusive experiments check if something else is running
        if exclusive and cls.activeExperiments != 0:
            Log.D(f"Resources denied to {executor}: Requests exclusive execution ({cls.activeExperiments} active)")
            return False

        # For non exclusive experiments check if an exclusive experiment is running
        if not exclusive and cls.activeExclusive is not None:
            Log.D(f"Resources denied to {executor}: Exclusive execution {cls.activeExclusive} in progress")
            return False

        # Check if some of the required resources are already locked
        for resource in resources:
            if resource.Locked:
                Log.D(f"Resources denied to {executor}: {resource.Id} already locked by {resource.Owner.ExecutionId}")
                return False

        # Check if some earlier experiment is requesting the same resources
        for key, values in cls.requesters.items():
            if key < executor:  # Check only older executors
                intersect = list(set(values) & set(resourceIds))
                if len(intersect) != 0:
                    Log.D(f"Resources denied to {executor} due to conflict with {key} ({intersect})")
                    return False

        # Try to lock all the required resources
        for id in resourceIds:
            success = cls.LockResource(id, owner)
            if success:
                lockedResources.append(id)
            if not success:
                Log.W(f"Could not lock resource '{id}'. Rolling back.")
                cls._releaseResources(lockedResources)
                return False

        if exclusive:
            cls.activeExclusive = owner.ExecutionId
        cls.activeExperiments += 1

        return True

    @classmethod
    @synchronized(lock)
    def ReleaseResources(cls, ids: List[str], owner: 'ExecutorBase'):
        execution = owner.ExecutionId
        _ = cls.requesters.pop(execution, None)
        cls._releaseResources(ids)

        if execution == cls.activeExclusive:
            cls.activeExclusive = None
        cls.activeExperiments -= 1

    @classmethod
    def _releaseResources(cls, ids: List[str]):
        for resource in ids:
            cls.ReleaseResource(resource)

    @classmethod
    def LockResource(cls, id: str, owner: 'ExecutorBase') -> bool:
        resource = cls.resources.get(id, None)
        if resource is not None:
            if not resource.Locked:
                resource.Owner = owner
                Log.I(f"Resource '{resource.Name}'({resource.Id}) locked by {resource.Owner.ExecutionId}")
                return True
            else:
                Log.E(f"Unable to lock resource '{resource.Name}'({resource.Id}) for run {owner.ExecutionId}, "
                      f"locked by '{resource.Owner.ExecutionId}")
        else:
            Log.E(f"Resource id {id} not found")
        return False

    @classmethod
    def ReleaseResource(cls, id: str) -> bool:
        resource = cls.resources.get(id, None)
        if resource is not None:
            if resource.Locked:
                Log.I(f"Releasing '{resource.Name}'({resource.Id}) "
                      f"(locked by '{resource.Owner.ExecutionId}'))")
                resource.Owner = None
                return True
            else:
                Log.W(f"Tried to release resource {id} while idle")
        else:
            Log.E(f"Resource id {id} not found")
        return False
