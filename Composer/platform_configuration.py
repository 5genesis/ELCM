from typing import Dict, List, ClassVar


class TaskDefinition:
    def __init__(self):
        self.Task: ClassVar = None
        self.Params: Dict = {}


class PlatformConfiguration:
    def __init__(self):
        self.PreRunParams = {}
        self.RunParams = {}
        self.PostRunParams = {}
        self.RunTasks: List[TaskDefinition] = []
