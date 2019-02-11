from Helper import Level
from typing import Dict
from datetime import datetime
from .status import Status
from .Tasks.PreRun import Configure, CheckAvailable, AddExperimentEntry
from .executor_base import ExecutorBase


class PreRunner(ExecutorBase):
    def __init__(self, params: Dict):
        super().__init__(params, "PreRunner")

    def Run(self):
        self.Log(Level.INFO, "Starting")
        self.Started = datetime.utcnow()
        self.api.NotifyStart(self.Id)
        self.Status = Status.Running

        Configure(self.Log).Start()
        CheckAvailable(self.Log).Start()
        AddExperimentEntry(self.Log).Start()

        self.Finished = datetime.utcnow()
        self.api.NotifyStop(self.Id)
        self.Log(Level.INFO, "Exited")
