from Facility import Facility, ActionInformation, DashboardPanel
from Data import ExperimentDescriptor, ExperimentType, NsInfo, Metal
from .platform_configuration import PlatformConfiguration, TaskDefinition
from importlib import import_module
from Helper import Log
from typing import List
from Executor.Tasks.Run import Message
from Interfaces import Management


class Composer:
    facility: Facility = None

    @classmethod
    def Compose(cls, descriptor: ExperimentDescriptor) -> PlatformConfiguration:
        def _messageAction(severity: str, message: str) -> ActionInformation:
            message = ActionInformation()
            message.TaskName = "Run.Message"
            message.Order = -9999
            message.Config = {'Severity': severity, 'Message': message}
            return message

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
                    flavor = sliceManager.GetNsdInfo(nsId)["flavor"]
                    nsInfo.Requirements = Metal(cpu=flavor["vcpu-count"],
                                                ram=flavor["memory-mb"],
                                                disk=flavor["storage-gb"])

                    configuration.NetworkServices.append(nsInfo)
                except Exception as e:
                    actions.append(
                        _messageAction("ERROR", f"Exception while obtaining information about network service {nsId}"))

        if descriptor.Type == ExperimentType.MONROE:
            actions.extend(cls.facility.GetMonroeActions())
        else:
            for ue in descriptor.UEs:
                actions.extend(cls.facility.GetUEActions(ue))
            for testcase in descriptor.TestCases:
                testcaseActions = cls.facility.GetTestCaseActions(testcase)
                if len(testcaseActions) != 0:
                    actions.extend(testcaseActions)
                else:
                    actions.append(_messageAction("ERROR", f'TestCase "{testcase}" did not generate any actions'))
                panels.extend(cls.facility.GetTestCaseDashboards(testcase))

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
