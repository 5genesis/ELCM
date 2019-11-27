from Task import Task
from Helper import Level
from time import sleep


class Report(Task):
    def __init__(self, logMethod, experimentName: str):
        super().__init__("Report", {'Name': experimentName}, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, f'Requesting Partial report for {self.params["Name"]}')
        sleep(3)
        self.Log(Level.INFO, 'Reporting completed')
