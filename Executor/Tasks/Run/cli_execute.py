from Task import Task
from Helper import Cli


class CliExecute(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("CLI Execute", parent, params, logMethod, None)
        self.paramRules = {
            'Parameters': (None, True),
            'CWD': (None, True)
        }

    def Run(self):
        cli = Cli(self.params['Parameters'], self.params['CWD'], self.logMethod)
        cli.Execute()
