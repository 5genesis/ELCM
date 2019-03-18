from Helper import Level
from typing import Dict
from datetime import datetime
from .status import Status
from .Tasks.PostRun import RequestResults, SaveResults, UpdateExperimentEntry
from .executor_base import ExecutorBase
from tempfile import TemporaryDirectory


class PostRunner(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "PostRunner", tempFolder)

    def Run(self):
        self.SetStarted()

        RequestResults(self.Log).Start()
        self.AddMessage('Results received', 30)
        SaveResults(self.Log).Start()
        self.AddMessage('Results stored', 60)
        UpdateExperimentEntry(self.Log).Start()
        self.AddMessage('Entry updated', 90)

        self.SetFinished(percent=100)
