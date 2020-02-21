from Task import Task
from Helper import Level
from time import sleep


class Message(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Message", parent, params, logMethod, None)

    def Run(self):
        level = Level[self.params['Severity']]
        self.Log(level, self.params['Message'])
