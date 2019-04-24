from Task import Task
from Helper import Tap


class TapExecute(Task):
    def __init__(self, logMethod, params):
        super().__init__("Tap Execute", params, logMethod, None)

    def Run(self):
        tapPlan = self.params['TestPlan']
        externals = self.params['Externals']

        tap = Tap(tapPlan, externals, self.logMethod)
        tap.Execute()


