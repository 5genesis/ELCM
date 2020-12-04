from REST import RestClient
from typing import List, Tuple, Dict, Optional
from Helper import Log
from time import sleep


class RemoteApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/distributed')

    def GetStatus(self, remoteId: int) -> Tuple[Optional['ExecutorStatus'], List[str]]:
        from Experiment import ExperimentStatus
        try:
            response = self.HttpGet(f'{self.api_url}/{remoteId}/status')
            data: Dict = self.ResponseToJson(response)
            if data['success']:
                return ExperimentStatus[data['status']], data['milestones']
            else:
                raise RuntimeError(data['message'])
        except Exception as e:
            Log.E(f"GetStatus error: {e}")
            return None, []

    def GetAllValues(self, remoteId: int) -> Dict[str, str]:
        try:
            response = self.HttpGet(f'{self.api_url}/{remoteId}/values')
            data: Dict = self.ResponseToJson(response)
            if data['success']:
                return data['values']
            else:
                raise RuntimeError(data['message'])
        except Exception as e:
            Log.E(f"GetAllValues error: {e}")
            return {}

    def GetValue(self, remoteId: int, name: str = None) -> Optional[str]:
        try:
            response = self.HttpGet(f'{self.api_url}/{remoteId}/values/{name}')
            data: Dict = self.ResponseToJson(response)
            if data['success']:
                return data['value']
            else:
                raise RuntimeError(data['message'])
        except Exception as e:
            Log.E(f"GetValue error: {e}")
            return None

    def GetResults(self, remoteId: int):
        pass

    def GetFiles(self, remoteId: int, outputPath: str) -> Optional[str]:
        retries = 5
        file = None
        while retries > 0 and file is None:
            file = self.DownloadFile(f"{self.api_url}/{remoteId}/files", outputPath)
            if file is None:
                retries -= 1
                sleep(5)
        return file


class ElcmDirect(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/api/v0')

    def ForceRun(self, descriptor: Dict) -> Optional[int]:
        from json import dumps
        url = f"{self.api_url}/run"
        response = self.HttpPost(url, extra_headers={'Content-Type': 'application/json'}, body=dumps(descriptor))
        return self.ResponseToJson(response).get('ExecutionId', None)
