from Task import Task
from Helper import Level


class Message(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Message", parent, params, logMethod, None)
        self.paramRules = {
            'Severity': ('INFO', False),
            'Message': (None, True)
        }

    def Run(self):
        level = Level[self.params['Severity']]
        self.Log(level, self.params['Message'])
