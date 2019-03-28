from Data import ExperimentDescriptor
from .platform_configuration import PlatformConfiguration
from importlib import import_module
from Helper import Log


class Composer:
    @staticmethod
    def Compose(descriptor: ExperimentDescriptor) -> PlatformConfiguration:
        name = 'PreRun.Configure'
        cls = Composer.GetTaskClass(name)
        configuration = PlatformConfiguration()
        configuration.RunParams['Report'] = {'ExperimentName': descriptor.Name}
        return configuration

    @staticmethod
    def GetTaskClass(taskName: str):
        try:
            packageName, className = taskName.split('.')
            package = import_module(f'Executor.Tasks.{packageName}')
            return getattr(package, className)
        except (ModuleNotFoundError, AttributeError, ValueError):
            Log.E(f'Task "{taskName}" not found')
            return None
