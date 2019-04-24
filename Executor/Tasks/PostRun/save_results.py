from Task import Task
from Helper import Level
from time import sleep


class SaveResults(Task):
    def __init__(self, logMethod):
        super().__init__("Save Results", None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Sending results to repo')
        sleep(3)
        self.Log(Level.INFO, 'Completed')
