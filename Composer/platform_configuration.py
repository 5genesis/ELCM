from typing import Dict, List, ClassVar, Dict
from Facility import DashboardPanel
from Data import NsInfo


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
        self.Requirements: List[str] = []
        self.NetworkServices: List[NsInfo] = []
        self.Nest: Optional[Dict] = None

    def ExpandDashboardPanels(self, experimentRun):
        from Experiment import Expander
        newPanels = []
        for panel in self.DashboardPanels:
            newPanel = DashboardPanel(Expander.ExpandDict(panel.AsDict(), context=experimentRun))
            newPanels.append(newPanel)
        self.DashboardPanels = newPanels