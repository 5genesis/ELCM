from typing import Dict
from .Tasks.PostRun import Decommission
from .executor_base import ExecutorBase
from tempfile import TemporaryDirectory


class PostRunner(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "PostRunner", tempFolder)

    def Run(self):
        self.SetStarted()

        Decommission(self.Log, self, self.Configuration.NetworkServices).Start()
        self.AddMessage('Resources decommisioned', 10)

        self.SetFinished(percent=100)
