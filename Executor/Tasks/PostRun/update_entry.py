from Task import Task
from Helper import Level
from time import sleep


class UpdateExecutionEntry(Task):
    def __init__(self, logMethod, parent):
        super().__init__("Update Execution Entry", parent, None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Sending entry information')
        sleep(1)
        self.Log(Level.INFO, 'Information sent')
