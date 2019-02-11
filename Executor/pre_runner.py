from Helper import Level
from typing import Dict
from datetime import datetime
from .status import Status
from .Tasks import Instantiate, Report, Decommission
from .executor_base import ExecutorBase


class PreRunner(ExecutorBase):
    def __init__(self, params: Dict):
        super().__init__(params, "PreRunner")

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
