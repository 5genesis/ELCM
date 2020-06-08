from typing import Dict
from .Tasks.PostRun import Decommission, ReleaseResources
from .executor_base import ExecutorBase
from tempfile import TemporaryDirectory


class PostRunner(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "PostRunner", tempFolder)

    def Run(self):
        self.SetStarted()

        Decommission(self.Log, self, self.Configuration.NetworkServices).Start()
        self.AddMessage('Network services decommisioned', 50)

        ReleaseResources(self.Log, self.Id, self.Configuration.Requirements, self).Start()
        self.AddMessage('Released resources', 90)

        self.SetFinished(percent=100)
