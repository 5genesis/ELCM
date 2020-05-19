from typing import Dict
from .Tasks.PostRun import RequestResults, SaveResults, UpdateExecutionEntry, Decommission
from .executor_base import ExecutorBase
from tempfile import TemporaryDirectory


class PostRunner(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "PostRunner", tempFolder)

    def Run(self):
        self.SetStarted()

        Decommission(self.Log, self, self.Configuration.NetworkServices).Start()
        self.AddMessage('Resources decommisioned', 10)

        RequestResults(self.Log, self).Start()
        self.AddMessage('Results received', 30)
        SaveResults(self.Log, self).Start()
        self.AddMessage('Results stored', 60)
        UpdateExecutionEntry(self.Log, self).Start()
        self.AddMessage('Entry updated', 90)

        self.SetFinished(percent=100)
