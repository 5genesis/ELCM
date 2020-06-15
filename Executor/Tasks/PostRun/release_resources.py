from Task import Task
from Helper import Level
from Interfaces import Management


class ReleaseResources(Task):
    def __init__(self, logMethod, id, requirements, parent):
        super().__init__("Release Resources", parent, {'Id': id, 'Available': False, 'Requirements': requirements},
                         logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Releasing resources')
        localRequirements = self.params["Requirements"]

        self.Log(Level.DEBUG, f'Local Requirements: {localRequirements}')
        Management.ReleaseLocalResources(self.parent, localRequirements)
