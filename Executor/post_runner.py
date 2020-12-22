from typing import Dict
from .Tasks.PostRun import Decommission, ReleaseResources, Farewell
from .executor_base import ExecutorBase
from tempfile import TemporaryDirectory


class PostRunner(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "PostRunner", tempFolder)

    def Run(self):
        self.SetStarted()

        Farewell(self.Log, self).Start()
        self.AddMessage('End coordination completed', 20)

        Decommission(self.Log, self, self.Configuration.NetworkServices).Start()
        self.AddMessage('Network services decommisioned', 50)

        ReleaseResources(self.Log, self.ExecutionId, self.Configuration.Requirements, self).Start()
        self.AddMessage('Released resources', 90)

        self.SetFinished(percent=100)
