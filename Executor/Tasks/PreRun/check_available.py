from Task import Task
from Helper import Level
from Interfaces import Management


class CheckAvailable(Task):
    def __init__(self, logMethod, id):
        super().__init__("Check Availability", {'Id': id, 'Available': False}, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Requesting availability')
        id = self.params['Id']
        available = Management.HasResources(id)
        self.params['Available'] = available
        self.Log(Level.INFO, f'Resources {"not" if not available else ""} available')
