from REST import RestClient
import json
from threading import Thread
from typing import Optional, Union


class DispatcherApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/api')

    def UpdateExecutionData(self, executionId: int,
                            status: Optional[str] = None, dashboardUrl: Optional[str] = None,
                            percent: Optional[int] = None, message: Optional[str] = None):

        Thread(target=self.updateAsync,
               args=(executionId, status, dashboardUrl, percent, message)).start()

    def updateAsync(self, executionId: int,
                    status: Optional[str], dashboardUrl: Optional[str],
                    percent: Optional[int], message: Optional[str]):

        def _maybeAdd(key: str, value: Union[str, int]):
            if value is not None: payload[key] = value

        url = f'{self.api_url}/execution/{executionId}'
        payload = {}

        _maybeAdd('Status', status)
        _maybeAdd('Dashboard', dashboardUrl)
        _maybeAdd('Percent', percent)
        _maybeAdd('Message', message)

        self.httpPatch(url, {'Content-Type': 'application/json'}, json.dumps(payload))
