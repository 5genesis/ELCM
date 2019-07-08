from Facility import Facility, ActionInformation, DashboardPanel
from Data import ExperimentDescriptor
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
        configuration.RunParams['Report'] = {'ExperimentName': descriptor.Name}

        instantiation = {'HasNsd': descriptor.HasNsd, 'ExperimentId': descriptor.Id }
        configuration.PreRunParams.update(instantiation)
        configuration.PostRunParams.update(instantiation)

        actions: List[ActionInformation] = []
        panels: List[DashboardPanel] = []
        for ue in descriptor.UEs.keys():
            actions.extend(cls.facility.GetUEActions(ue))
        for testcase in descriptor.TestCases:
            actions.extend(cls.facility.GetTestCaseActions(testcase))
            panels.extend(cls.facility.GetTestCaseDashboards(testcase))

        actions.sort(key=lambda action: action.Order)  # Sort by Order

        for action in actions:
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
