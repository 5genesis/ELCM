from random import randrange
from REST import RestClient
from Helper import Config
from typing import Dict, Optional, Tuple, List
from Data import Metal, NsInfo
from Facility import Facility


class Management:
    sliceManager = None

    @classmethod
    def HasResources(cls, owner: 'ExecutorBase', localResources: List[str], networkServices: List[NsInfo]):
        # TODO: handle NS first

        return Facility.TryLockResources(localResources, owner)

    @classmethod
    def SliceManager(cls):
        if cls.sliceManager is None:
            settings = Config().SliceManager
            cls.sliceManager = SliceManager(settings.Host, settings.Port)
        return cls.sliceManager


class SliceManager(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, "/api")

    def CreateSlice(self, nsd: str) -> str:
        response = self.httpPost(f"{self.api_url}/slice", {"Content-Type": "application/json"}, nsd)
        return response.data.decode('utf-8')

    def CheckSlice(self, slice: str) -> Dict:
        response = self.httpGet(f"{self.api_url}/slice/{slice}", {"Accept": "application/json"})
        return self.responseToJson(response)

    def SliceCreationTime(self, slice: str) -> Dict:
        response = self.httpGet(f"{self.api_url}/slice/{slice}/time", {"Accept": "application/json"})
        return self.responseToJson(response)

    def DeleteSlice(self, slice: str) -> str:
        response = self.httpDelete(f"{self.api_url}/slice/{slice}")
        return response.data.decode('utf-8')

    def GetNsdInfo(self, nsd: str) -> Dict:
        response = self.httpGet(f"{self.api_url}/api/nslist?nsd-id={nsd} ")
        return self.responseToJson(response)
