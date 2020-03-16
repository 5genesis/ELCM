from Task import Task
from Helper import Level
from time import sleep


class RequestResults(Task):
    def __init__(self, logMethod, parent):
        super().__init__("Request Results", parent, None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Requesting execution results')
        sleep(1)
        self.Log(Level.INFO, 'Completed')
