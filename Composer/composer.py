from Facility import Facility, ActionInformation, DashboardPanel
from Data import ExperimentDescriptor, ExperimentType, NsInfo, Metal
from .platform_configuration import PlatformConfiguration, TaskDefinition
from importlib import import_module
from Helper import Log
from typing import List, Dict
from Executor.Tasks.Run import Message
from Interfaces import Management


class Composer:
    facility: Facility = None

    @classmethod
    def Compose(cls, descriptor: ExperimentDescriptor) -> PlatformConfiguration:
        def _messageAction(severity: str, message: str) -> ActionInformation:
            action = ActionInformation()
            action.TaskName = "Run.Message"
            action.Order = -9999
            action.Config = {'Severity': severity, 'Message': message}
            return action

        def _messageTask(severity: str, message: str) -> TaskDefinition:
            task = TaskDefinition()
            task.Task = Message
            task.Params = {'Severity': severity, 'Message': message}
            return task

        if cls.facility is None:
            cls.facility = Facility()

        configuration = PlatformConfiguration()
        configuration.RunParams['Report'] = {'ExperimentName': descriptor.Identifier}

        actions: List[ActionInformation] = []
        panels: List[DashboardPanel] = []

        if len(descriptor.NetworkServices) != 0:
            sliceManager = Management.SliceManager()
            for ns in descriptor.NetworkServices:
                nsId, location = ns
                try:
                    nsInfo = NsInfo(nsId, location)
                    requirements = sliceManager.GetNsdRequirements(nsId)
                    if requirements is None:
                        raise RuntimeError("Could not retrieve NSD information")
                    nsInfo.Requirements = requirements
                    configuration.NetworkServices.append(nsInfo)
                except Exception as e:
                    actions.append(
                        _messageAction("ERROR",
                                       f"Exception while obtaining information about network service {nsId}: {e}"))

        if len(configuration.NetworkServices) != 0:  # At least one NSD info was successfully retrieved
            configuration.Nest = cls.composeNest(descriptor.Slice, descriptor.Scenario, configuration.NetworkServices)

        if descriptor.Type == ExperimentType.MONROE:
            actions.extend(cls.facility.GetMonroeActions())
        else:
            if descriptor.Automated:
                for ue in descriptor.UEs:
                    actions.extend(cls.facility.GetUEActions(ue))
                for testcase in descriptor.TestCases:
                    testcaseActions = cls.facility.GetTestCaseActions(testcase)
                    if len(testcaseActions) != 0:
                        actions.extend(testcaseActions)
                    else:
                        actions.append(_messageAction("ERROR", f'TestCase "{testcase}" did not generate any actions'))
                    panels.extend(cls.facility.GetTestCaseDashboards(testcase))
            else:
                delay = ActionInformation()
                delay.TaskName = "Run.Delay"
                delay.Config = {'Time': descriptor.Duration*60}
                actions.append(delay)

        actions.sort(key=lambda action: action.Order)  # Sort by Order
        requirements = set()

        for action in actions:
            requirements.update(action.Requirements)

            task = cls.getTaskClass(action.TaskName)
            if task is None:
                taskDefinition = _messageTask("ERROR", f"Could not find task {action.TaskName}")
            else:
                taskDefinition = TaskDefinition()
                taskDefinition.Params = action.Config
                taskDefinition.Task = task
            configuration.RunTasks.append(taskDefinition)

        configuration.Requirements = list(requirements)
        configuration.DashboardPanels = panels

        return configuration

    @staticmethod
    def getTaskClass(taskName: str):
        try:
            packageName, className = taskName.split('.')
            package = import_module(f'Executor.Tasks.{packageName}')
            return getattr(package, className)
        except (ModuleNotFoundError, AttributeError, ValueError):
            Log.E(f'Task "{taskName}" not found')
            return None

    @classmethod
    def composeNest(cls, baseSlice: str, scenario: str, nss: List[NsInfo]) -> Dict:
        # TODO: Handle scenario
        nsList = []
        for ns in nss:
            nsList.append({
                "nsd-id": ns.Id,
                "placement": ns.Location,
            })

        return {
            "base_slice_descriptor": {
                "base_slice_des_id": baseSlice
            },
            "service_descriptor": {
                "ns_list": nsList
            }
        }




