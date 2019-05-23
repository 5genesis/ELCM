from typing import Dict, List, ClassVar
from Facility import DashboardPanel



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
        self.DashboardPanels: List[DashboardPanel] = []

    def ExpandDashboardPanels(self, experiment):
        from Experiment import Expander
        newPanels = []
        for panel in self.DashboardPanels:
            newPanel = DashboardPanel(Expander.ExpandDict(panel.AsDict(), context=experiment))
            newPanels.append(newPanel)
        self.DashboardPanels = newPanels