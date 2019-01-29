from Helper import Child, Level
from typing import Dict
from time import sleep
from datetime import datetime


class Executor(Child):
    def __init__(self, params: Dict):
        super().__init__(f"Executor{datetime.now().strftime('%y%m%d%H%M%S%f')}")
        self.params = params

    def Run(self):
            sleep(10)

