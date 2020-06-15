from Task import Task
from Helper import Level
from Data import NsInfo
from typing import List
from Interfaces import Management


class Decommission(Task):
    def __init__(self, logMethod, parent, networkServices):
        super().__init__("Decommission", parent, {'NetworkServices': networkServices}, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Decommision started')
        networkServices: List[NsInfo] = self.params['NetworkServices']
        if len(networkServices) != 0:
            self.Log(Level.INFO, f"Experiment has {len(networkServices)} network services")
            for ns in networkServices:
                self.Log(Level.INFO, f"Requesting decommision of NS {ns.Id} with slice ID: {ns.SliceId}")
                try:
                    # TODO
                    self.Log(Level.INFO, f'Slice decommisioned')
                except Exception as e:
                    raise Exception(f'Exception while decommisioning slice: {e}') from e
        else:
            self.Log(Level.INFO, 'Decommision not required, no NSD IDs defined.')
        self.Log(Level.INFO, 'Decommision completed')
