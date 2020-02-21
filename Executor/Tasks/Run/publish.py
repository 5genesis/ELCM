from Task import Task
from Helper import Level
from time import sleep


class Publish(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Publish", parent, params, logMethod, None)

    def Run(self):
        for key, value in self.params.items():
            self.Publish(key, value)
