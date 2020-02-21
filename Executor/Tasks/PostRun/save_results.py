from Task import Task
from Helper import Level
from time import sleep


class SaveResults(Task):
    def __init__(self, logMethod, parent):
        super().__init__("Save Results", parent, None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Sending results to repo')
        sleep(1)
        self.Log(Level.INFO, 'Completed')
