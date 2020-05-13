from Task import Task
from Helper import Level
from Interfaces import Management


class Decommission(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Decommission", parent, params, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Decommision started')
        networkServices = self.params['NetworkServices']
        if len(networkServices) != 0:
            sliceIds = self.params['SliceIds']
            self.Log(Level.INFO, f"Experiment has instantiated slices: {sliceIds}")
            for slice in sliceIds:
                self.Log(Level.INFO, f"Requesting decommision of slice: {slice}")
                try:
                    # TODO
                    self.Log(Level.INFO, f'Slice decommisioned')
                except Exception as e:
                    raise Exception(f'Exception while decommisioning slice: {e}') from e
        else:
            self.Log(Level.INFO, 'Decommision not required, no NSD IDs defined.')
        self.Log(Level.INFO, 'Decommision completed')
