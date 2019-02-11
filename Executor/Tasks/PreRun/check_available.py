from Task import Task
from Helper import Level
from time import sleep


class CheckAvailable(Task):
    def __init__(self, logMethod):
        super().__init__("Check Availability", None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Requesting availability')
        sleep(3)
        self.Log(Level.INFO, 'Completed')
