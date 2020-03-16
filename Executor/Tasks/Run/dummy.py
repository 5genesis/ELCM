from Task import Task
from Helper import Level
from time import sleep


class Dummy(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Dummy", parent, params, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, f'Running Dummy task with params: {self.params}')
