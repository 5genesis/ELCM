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
            sliceId = networkServices[0].SliceId  # All NS should share the same slice ID
            if sliceId is not None:
                self.Log(Level.INFO, f"Experiment has {len(networkServices)} network services with slice ID: {sliceId}."
                                     f"Requesting decommision")
                try:
                    message, success = Management.SliceManager().DeleteSlice(sliceId)
                    if success:
                        self.Log(Level.INFO, f'Slice decommisioned')
                    else:
                        self.Log(Level.ERROR, message)
                except Exception as e:
                    raise Exception(f'Exception while decommisioning slice: {e}') from e
            else:
                self.Log(Level.WARNING, 'Experiment contains network services, but no slice ID. '
                                        'Please review the Pre-Run log for instantiation issues.')
        else:
            self.Log(Level.INFO, 'Decommision not required, no Network Services defined.')
        self.Log(Level.INFO, 'Decommision completed')
