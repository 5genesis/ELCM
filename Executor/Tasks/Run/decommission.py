from Task import Task
from Helper import Level
from time import sleep


class Decommission(Task):
    def __init__(self, logMethod):
        super().__init__("Decommission", None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Decommissioning resources')
        sleep(3)
        self.Log(Level.INFO, 'Decommision completed')
