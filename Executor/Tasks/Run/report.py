from Task import Task
from Helper import Level
from time import sleep


class Report(Task):
    def __init__(self, logMethod):
        super().__init__("Report", None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Requesting Partial report')
        sleep(3)
        self.Log(Level.INFO, 'Reporting completed')
