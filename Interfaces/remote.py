from REST import RestClient
from typing import List, Tuple, Dict, Optional
from Helper import Log


class RemoteApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/distributed')

    def GetStatus(self, remoteId: int) -> Tuple[Optional['ExecutorStatus'], List[str]]:
        from Executor import ExecutorStatus
        try:
            response = self.HttpGet(f'/{remoteId}/status')
            data: Dict = self.ResponseToJson(response)
            if data['success']:
                return ExecutorStatus[data['status']], data['milestones']
            else:
                raise RuntimeError(data['message'])
        except Exception as e:
            Log.E(f"GetStatus error: {e}")
            return None, []

    def GetAllValues(self, remoteId: int) -> Dict[str, str]:
        try:
            response = self.HttpGet(f'/{remoteId}/values')
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
            response = self.HttpGet(f'/{remoteId}/values/{name}')
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
