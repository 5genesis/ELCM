from Helper import Child, Level
from typing import Dict
from time import sleep
from datetime import datetime
from .api import Api
from enum import Enum, unique

@unique
class Status(Enum):
    Init, Running, Cancelled, Errored, Finished = range(5)


class Executor(Child):
    api = None

    def __init__(self, params: Dict):
        super().__init__(f"Executor{datetime.now().strftime('%y%m%d%H%M%S%f')}")
        self.params = params
        self.Id = params['Id']
        self.Started = None
        self.Status = Status.Init

        if self.api is None: self.api=Api('127.0.0.1', '5000')

    def Run(self):
        self.Log(Level.INFO, "Starting")
        self.Started = datetime.utcnow()
        self.api.NotifyStart(self.Id)
        self.Status = Status.Running
        for _ in range(1, 30):
            if self.stopRequested:
                self.Log(Level.INFO, "Received stop request, exiting")
                self.Status = Status.Cancelled
                break
            self.Log(Level.DEBUG, 'Ping')
            sleep(1)
        self.api.NotifyStop(self.Id)
        self.Status = Status.Finished
        self.Log(Level.INFO, "Exited")


