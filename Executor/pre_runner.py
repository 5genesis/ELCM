from Helper import Level
from typing import Dict
from datetime import datetime
from .status import Status
from .Tasks.PreRun import Configure, CheckAvailable, AddExperimentEntry
from .executor_base import ExecutorBase
from tempfile import TemporaryDirectory
from time import sleep


class PreRunner(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "PreRunner", tempFolder)

    def Run(self):
        self.LogAndMessage(Level.INFO, "Starting")
        self.Started = datetime.utcnow()
        self.Status = Status.Running

        Configure(self.Log).Start()
        self.AddMessage("Configuration completed", 30)
        available = False
        while not available:
            result = CheckAvailable(self.Log, self.Id).Start()
            available = result['Available']
            if not available:
                self.AddMessage('Not available')
                sleep(10)

        self.AddMessage('Resources granted', 80)
        AddExperimentEntry(self.Log).Start()
        self.AddMessage('Experiment registered', 80)

        self.Finished = datetime.utcnow()
        self.Log(Level.INFO, "Exited")
