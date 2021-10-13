from Task import Task
from Helper import Level


class AddMilestone(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Add Milestone", parent, params, logMethod, None)
        self.paramRules = {'Milestone': (None, True)}

    def Run(self):
        milestone = self.params['Milestone']
        self.Log(Level.INFO, f"Adding milestone '{milestone}' to experiment.")
        self.parent.AddMilestone(milestone)
