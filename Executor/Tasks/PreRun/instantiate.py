from Task import Task
from Helper import Level, Config
from Interfaces import Management, PortalApi


class Instantiate(Task):
    def __init__(self, logMethod, tempFolder, parent, params):
        super().__init__("Instantiate", parent, params, logMethod, None)
        self.tempFolder = tempFolder

    def Run(self):
        networkServices = self.params['NetworkServices']
        sliceIds = []

        if len(networkServices) != 0:
            self.Log(Level.INFO, f"Experiment contains NSD IDs: {networkServices}")
            for ns in networkServices:
                self.Log(Level.INFO, f"Requesting instantiation of NSD: {ns}")
                try:
                    # sliceId = Management.SliceManager().Create(nsdContent)
                    sliceId = "placeholder"  # TODO
                    self.Log(Level.INFO, f'Network service instantiated with ID: {sliceId}')
                    sliceIds.append(sliceId)
                except Exception as e:
                    raise Exception(f'Exception while creating slice: {e}') from e
        else:
            self.Log(Level.INFO, 'Instantiation not required, no NSD IDs defined.')

        self.Log(Level.INFO, 'Instantiation completed')
        self.params["SliceIds"] = sliceIds
