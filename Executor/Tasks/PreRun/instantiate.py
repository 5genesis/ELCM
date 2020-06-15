from Task import Task
from Helper import Level, Config
from Data import NsInfo
from typing import List


class Instantiate(Task):
    def __init__(self, logMethod, tempFolder, parent, networkServices):
        super().__init__("Instantiate", parent, {'NetworkServices': networkServices}, logMethod, None)
        self.tempFolder = tempFolder

    def Run(self):
        networkServices: List[NsInfo] = self.params['NetworkServices']  # TODO: this is List[NsInfo] now
        sliceIds = []

        if len(networkServices) != 0:
            self.Log(Level.INFO, f"Experiment contains {len(networkServices)} NSD IDs")
            for ns in networkServices:
                self.Log(Level.INFO, f"Requesting instantiation of NSD: {ns.Id}")
                try:
                    # sliceId = Management.SliceManager().CreateSlice(nsdContent)
                    sliceId = "placeholder"  # TODO
                    self.Log(Level.INFO, f'Network service instantiated with ID: {sliceId}')
                    ns.SliceId = sliceId
                except Exception as e:
                    raise Exception(f'Exception while creating slice: {e}') from e
        else:
            self.Log(Level.INFO, 'Instantiation not required, no NSD IDs defined.')

        self.Log(Level.INFO, 'Instantiation completed')
        self.params["SliceIds"] = sliceIds
