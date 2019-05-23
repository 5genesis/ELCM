from REST import RestClient
import json
from threading import Thread
from typing import Optional


class DispatcherApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/api')

    def UpdateExecutionData(
            self, executionId: int, status: Optional[str] = None, dashboardUrl: Optional[str] = None):
        Thread(target=self.updateAsync, args=(executionId, status, dashboardUrl)).start()

    def updateAsync(self, executionId: int, status: Optional[str], dashboardUrl: Optional[str]):
        url = f'{self.api_url}/execution/{executionId}'
        payload = {}
        if status is not None:
            payload['Status'] = status
        if dashboardUrl is not None:
            payload['Dashboard'] = dashboardUrl
        self.httpPatch(url, {'Content-Type': 'application/json'}, json.dumps(payload))
