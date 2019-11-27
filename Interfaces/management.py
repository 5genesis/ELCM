from random import randrange
from REST import RestClient
from Helper import Config
from typing import Dict


class Management:
    registry = {}
    sliceManager = None

    @classmethod
    def HasResources(cls, executorId):
        if executorId not in cls.registry.keys():
            cls.registry[executorId] = randrange(0, 3)
        if cls.registry[executorId] == 0:
            cls.registry.pop(executorId)
            return True
        else:
            cls.registry[executorId] -= 1
            return False

    @classmethod
    def SliceManager(cls):
        if cls.sliceManager is None:
            settings = Config().SliceManager
            cls.sliceManager = SliceManager(settings.Host, settings.Port)
        return cls.sliceManager


class SliceManager(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, "/api")

    def Create(self, nsd: str) -> str:
        response = self.httpPost(f"{self.api_url}/slice", {"Content-Type": "application/json"}, nsd)
        return response.data.decode('utf-8')

    def Check(self, slice: str) -> Dict:
        response = self.httpGet(f"{self.api_url}/slice/{slice}", {"Accept": "application/json"})
        return self.responseToJson(response)

    def Time(self, slice: str) -> Dict:
        response = self.httpGet(f"{self.api_url}/slice/{slice}/time", {"Accept": "application/json"})
        return self.responseToJson(response)

    def Delete(self, slice: str) -> str:
        response = self.httpDelete(f"{self.api_url}/slice/{slice}")
        return response.data.decode('utf-8')
