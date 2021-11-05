from REST import RestClient
import json
from threading import Thread
from typing import Optional, Union
from Settings.config import Portal as PortalConfig


class PortalApi(RestClient):
    def __init__(self, config: PortalConfig):
        self.Enabled = config.Enabled
        super().__init__(config.Host, config.Port, '/api')

    def UpdateExecutionData(self, executionId: int,
                            status: Optional[str] = None, dashboardUrl: Optional[str] = None,
                            percent: Optional[int] = None, message: Optional[str] = None):
        if self.Enabled:
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
        _maybeAdd('PerCent', percent)
        _maybeAdd('Message', message)

        self.HttpPatch(url, {'Content-Type': 'application/json'}, json.dumps(payload))
