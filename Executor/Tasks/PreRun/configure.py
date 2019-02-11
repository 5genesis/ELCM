from Task import Task
from Helper import Level
from time import sleep


class Configure(Task):
    def __init__(self, logMethod):
        super().__init__("Configure", None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Requesting configuration')
        sleep(3)
        self.Log(Level.INFO, 'Configuration completed')
