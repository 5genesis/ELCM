from Data import ExperimentDescriptor
from .platform_configuration import PlatformConfiguration, TaskDefinition
from importlib import import_module
from Helper import Log
from typing import List, Dict
import yaml
from sys import maxsize


class Composer:
    facility: Dict = None

    @classmethod
    def Compose(cls, descriptor: ExperimentDescriptor) -> PlatformConfiguration:
        if cls.facility is None:
            with open('facility.yml', 'r', encoding='utf-8') as file:
                cls.facility = yaml.load(file)

        name = 'PreRun.Configure'
        configuration = PlatformConfiguration()
        configuration.RunParams['Report'] = {'ExperimentName': descriptor.Name}

        actions: List[Dict] = []
        for ue in descriptor.UEs.keys():
            actions.extend(cls.getUEActions(ue))
        for testcase in descriptor.TestCases:
            actions.extend(cls.getTestCaseActions(testcase))

        actions.sort(key=lambda action: action.get('Order', maxsize))  # Sort by Order, leave at end if key is not found

        for action in actions:
            taskDefinition = TaskDefinition()
            taskDefinition.Task = cls.getTaskClass(action['Task'])
            if 'Config' in action.keys():
                taskDefinition.Params = action['Config']
            configuration.RunTasks.append(taskDefinition)

        return configuration

    @classmethod
    def getUEActions(cls, id: str) -> List[Dict]:
        return cls.getFromSection('UEs', id)

    @classmethod
    def getTestCaseActions(cls, id: str) -> List[Dict]:
        return cls.getFromSection('TestCases', id)

    @classmethod
    def getFromSection(cls, section: str, id: str) -> List[Dict]:
        if section in cls.facility.keys() and id in cls.facility[section].keys():
            return cls.facility[section][id]
        return []

    @staticmethod
    def getTaskClass(taskName: str):
        try:
            packageName, className = taskName.split('.')
            package = import_module(f'Executor.Tasks.{packageName}')
            return getattr(package, className)
        except (ModuleNotFoundError, AttributeError, ValueError):
            Log.E(f'Task "{taskName}" not found')
            return None
