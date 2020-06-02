from Facility import Facility, ActionInformation, DashboardPanel
from Data import ExperimentDescriptor, ExperimentType, NsInfo
from .platform_configuration import PlatformConfiguration, TaskDefinition
from importlib import import_module
from Helper import Log
from typing import List
from Executor.Tasks.Run import Message


class Composer:
    facility: Facility = None

    @classmethod
    def Compose(cls, descriptor: ExperimentDescriptor) -> PlatformConfiguration:
        if cls.facility is None:
            cls.facility = Facility()

        configuration = PlatformConfiguration()
        configuration.RunParams['Report'] = {'ExperimentName': descriptor.Identifier}

        for ns in descriptor.NetworkServices:
            configuration.NetworkServices.append(NsInfo(ns))

        actions: List[ActionInformation] = []
        panels: List[DashboardPanel] = []

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
                    message = ActionInformation()
                    message.TaskName = "Run.Message"
                    message.Order = -9999
                    message.Config = {'Severity': 'ERROR',
                                      'Message': f'TestCase "{testcase}" did not generate any actions'}
                    actions.append(message)
                panels.extend(cls.facility.GetTestCaseDashboards(testcase))

        actions.sort(key=lambda action: action.Order)  # Sort by Order
        requirements = set()

        for action in actions:
            requirements.update(action.Requirements)

            taskDefinition = TaskDefinition()
            taskDefinition.Params = action.Config
            task = cls.getTaskClass(action.TaskName)
            if task is None:
                taskDefinition.Task = Message
                taskDefinition.Params['Severity'] = "ERROR"
                taskDefinition.Params['Message'] = f"Could not find task {action.TaskName}"
            else:
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
