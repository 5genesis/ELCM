from Facility import Facility
from Data import ExperimentDescriptor
from .platform_configuration import PlatformConfiguration, TaskDefinition
from importlib import import_module
from Helper import Log
from typing import List, Dict
import yaml
from sys import maxsize


class Composer:
    facility: Facility = None

    @classmethod
    def Compose(cls, descriptor: ExperimentDescriptor) -> PlatformConfiguration:
        if cls.facility is None:
            cls.facility = Facility()

        name = 'PreRun.Configure'
        configuration = PlatformConfiguration()
        configuration.RunParams['Report'] = {'ExperimentName': descriptor.Name}

        actions: List[Dict] = []
        for ue in descriptor.UEs.keys():
            actions.extend(cls.facility.GetUEActions(ue))
        for testcase in descriptor.TestCases:
            actions.extend(cls.facility.GetTestCaseActions(testcase))

        actions.sort(key=lambda action: action.get('Order', maxsize))  # Sort by Order, leave at end if key is not found

        for action in actions:
            taskDefinition = TaskDefinition()
            taskDefinition.Task = cls.getTaskClass(action['Task'])
            if 'Config' in action.keys():
                taskDefinition.Params = action['Config']
            configuration.RunTasks.append(taskDefinition)

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
