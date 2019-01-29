from Helper import Child, Level
from typing import Dict
from time import sleep
from datetime import datetime
from .api import Api


class Executor(Child):
    api = None

    def __init__(self, params: Dict):
        super().__init__(f"Executor{datetime.now().strftime('%y%m%d%H%M%S%f')}")
        self.params = params
        self.Id = params['Id']

        if self.api is None: self.api=Api('127.0.0.1', '5000')

    def Run(self):
        self.api.NotifyStart(self.Id)
        sleep(10)
        self.api.NotifyStop(self.Id)

