from Task import Task
from Helper import Level
from Settings import Config
from Data import NsInfo
from typing import List, Dict
from Interfaces import Management
from json import dumps


class Instantiate(Task):
    def __init__(self, logMethod, tempFolder, parent, networkServices, nest, baseSlice):
        super().__init__("Instantiate", parent, {'NetworkServices': networkServices, 'NEST': nest, 'Slice': baseSlice},
                         logMethod, None)
        self.tempFolder = tempFolder

    def Run(self):
        baseSlice: str = self.params['Slice']
        networkServices: List[NsInfo] = self.params['NetworkServices']
        nest: Dict = self.params['NEST']

        if baseSlice is not None:
            self.Log(Level.INFO, f"Experiment contains {len(networkServices)} NSD IDs over Base Slice '{baseSlice}'. "
                                 f"Requesting instantiation.")
            self.Log(Level.DEBUG, f"NEST: '{nest}'")
            maybeSliceId, success = Management.SliceManager().CreateSlice(dumps(nest))
            if success:
                self.params['DeployedSliceId'] = maybeSliceId
                for ns in networkServices:
                    ns.SliceId = maybeSliceId
            else:
                self.Log(Level.ERROR, maybeSliceId)
        else:
            self.Log(Level.INFO, 'Instantiation not required, base slice not defined.')

        self.Log(Level.INFO, 'Instantiation completed')
