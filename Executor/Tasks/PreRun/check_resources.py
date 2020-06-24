from Task import Task
from Helper import Level
from Interfaces import Management


class CheckResources(Task):
    def __init__(self, logMethod, id, requirements, networkServices, parent):
        super().__init__("Check Resources", parent, {'Id': id, 'Available': False, 'Requirements': requirements,
                                                     'NetworkServices': networkServices}, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Trying to lock resources')
        localRequirements = self.params["Requirements"]
        networkServices = self.params["NetworkServices"]
        exclusive = self.parent.Descriptor.Exclusive

        self.Log(Level.DEBUG, f'Local Requirements: {localRequirements}')
        if len(networkServices) != 0:
            self.Log(Level.DEBUG, f'NS Requirements: {networkServices}')

        available, feasible = Management.HasResources(self.parent, localRequirements, networkServices, exclusive)
        self.params['Available'] = available
        self.params['Feasible'] = feasible
        self.Log(Level.INFO, f'Resources {"not" if not available else ""} available')
