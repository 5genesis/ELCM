from Helper import Child, Level
from typing import Dict
from datetime import datetime
from .executor_base import ExecutorBase
from .Tasks.Run import Instantiate, Report, Decommission
from .status import Status
from tempfile import TemporaryDirectory


class Executor(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "Executor", tempFolder)

    def Run(self):
        self.Log(Level.INFO, "Starting")
        self.Started = datetime.utcnow()
        self.api.NotifyStart(self.Id)
        self.Status = Status.Running

        Instantiate(self.Log).Start()

        for _ in range(1, 3):
            if self.stopRequested:
                self.Log(Level.INFO, "Received stop request, exiting")
                self.Status = Status.Cancelled
                break
            Report(self.Log).Start()
        else:
            self.Status = Status.Finished

        Decommission(self.Log).Start()

        self.Finished = datetime.utcnow()
        self.api.NotifyStop(self.Id)
        self.Log(Level.INFO, "Exited")
