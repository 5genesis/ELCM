from Task import Task
from Helper import Level
from Data import NsInfo
from typing import List
from Interfaces import Management


class Decommission(Task):
    def __init__(self, logMethod, parent, deployedSliceId, networkServices):
        super().__init__("Decommission", parent,
                         {'DeployedSliceId': deployedSliceId, 'NetworkServices': networkServices}, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Decommision started')
        deployedSliceId: str = self.params['DeployedSliceId']
        networkServices: List[NsInfo] = self.params['NetworkServices']
        if deployedSliceId is not None:
            self.Log(Level.INFO, f"Experiment has {len(networkServices)} network services with "
                                 f"slice ID: {deployedSliceId}. Requesting decommision")
            try:
                message, success = Management.SliceManager().DeleteSlice(deployedSliceId)
                if success:
                    self.Log(Level.INFO, f'Slice decommisioned')
                else:
                    self.Log(Level.ERROR, message)
            except Exception as e:
                raise Exception(f'Exception while decommisioning slice: {e}') from e
        else:
            self.Log(Level.INFO, 'Decommision not required, no Slice deployed.')
        self.Log(Level.INFO, 'Decommision completed')
