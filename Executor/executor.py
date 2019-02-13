from Helper import Child, Level
from typing import Dict
from datetime import datetime
from time import sleep
from .executor_base import ExecutorBase
from .Tasks.Run import Instantiate, Report, Decommission
from .status import Status
from tempfile import TemporaryDirectory
from random import randint
from math import floor


class Executor(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "Executor", tempFolder)

    def Run(self):
        self.LogAndMessage(Level.INFO, "Starting")
        self.Started = datetime.utcnow()
        self.api.NotifyStart(self.Id)
        self.Status = Status.Running

        Instantiate(self.Log).Start()
        self.AddMessage('Instantiation completed', 10)

        loops = randint(3, 6)
        for i in range(1, loops):
            if self.stopRequested:
                self.LogAndMessage(Level.INFO, "Received stop request, exiting")
                self.Status = Status.Cancelled
                break
            Report(self.Log).Start()
            sleep(1)
            self.AddMessage('Experiment running...', int(floor(10+((i/loops)*80))))
        else:
            self.Status = Status.Finished

        Decommission(self.Log).Start()
        self.AddMessage('Decommision completed', 100)

        self.Finished = datetime.utcnow()
        self.api.NotifyStop(self.Id)
        self.LogAndMessage(Level.INFO, "Exited")
