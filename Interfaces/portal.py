from REST import RestClient
from typing import Optional
from Helper import Log


class PortalApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '')

    def DownloadNsd(self, experimentId: int, outputFolder: str) -> Optional[str]:
        url = f"{self.api_url}/experiment/{experimentId}/nsdFile"
        try:
            file = self.DownloadFile(url, outputFolder)
        except KeyError:
            Log.D(f"Experiment Id {experimentId} does not have NSD file")
            return None
        except Exception as e:
            Log.E(f"Exception while retrieving NSD file (Experiment {experimentId}): {e}")
            return None
        return file
