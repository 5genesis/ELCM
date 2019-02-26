from REST import RestClient
import json
from threading import Thread


class DispatcherApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/api/executor')

    def UpdateStatus(self, executionId: int, status: str):
        Thread(target=self.updateAsync, args=(executionId, status)).start()

    def updateAsync(self, executionId: int, status: str):
        url = f'{self.api_url}/execution/{executionId}'
        self.httpPatch(url, None, json.dumps({'Status': status}))
