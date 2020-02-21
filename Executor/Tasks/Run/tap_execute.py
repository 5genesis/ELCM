from Task import Task
from Helper import Tap, Config, Level


class TapExecute(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Tap Execute", parent, params, logMethod, None)

    def Run(self):
        if not Config().Tap.Enabled:
            self.Log(Level.CRITICAL, "Trying to run TapExecute Task while TAP is not enabled")
        else:
            tapPlan = self.params['TestPlan']
            externals = self.params.get('Externals', {})

            tap = Tap(tapPlan, externals, self.logMethod)
            tap.Execute()


