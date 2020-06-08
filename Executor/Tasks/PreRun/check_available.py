from Task import Task
from Helper import Level
from Interfaces import Management


class CheckAvailable(Task):
    def __init__(self, logMethod, id, requirements, networkServices, parent):
        super().__init__("Check Availability", parent, {'Id': id, 'Available': False, 'Requirements': requirements,
                          'NetworkServices': networkServices}, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Requesting availability')
        localRequirements = self.params["Requirements"]
        networkServices = self.params["NetworkServices"]

        self.Log(Level.DEBUG, f'Local Requirements: {localRequirements}')
        if len(networkServices) != 0:
            self.Log(Level.DEBUG, f'NS Requirements: {networkServices}')

        available = Management.HasResources(self.parent, localRequirements, networkServices)
        self.params['Available'] = available
        self.Log(Level.INFO, f'Resources {"not" if not available else ""} available')
