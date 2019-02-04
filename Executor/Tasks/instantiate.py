from Task import Task
from Helper import Level
from time import sleep


class Instantiate(Task):
    def __init__(self, logMethod):
        super().__init__("Instantiate", None, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Requesting resources to MANO layer')
        sleep(3)
        self.Log(Level.INFO, 'Instantiation completed')
