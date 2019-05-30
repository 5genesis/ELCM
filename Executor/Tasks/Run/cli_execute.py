from Task import Task
from Helper import Cli


class CliExecute(Task):
    def __init__(self, logMethod, params):
        super().__init__("CLI Execute", params, logMethod, None)

    def Run(self):
        parameters = self.params['Parameters']
        cwd = self.params['CWD']

        cli = Cli(parameters, cwd, self.logMethod)
        cli.Execute()
