from REST import RestClient
from Executor import ExecutorStatus
from typing import List, Tuple, Dict, Optional


class RemoteApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, '/distributed')

    def GetStatus(self, remoteId: int) -> Tuple[Optional[ExecutorStatus], List[str]]:
        pass

    def GetAllValues(self, remoteId: int, name: str = None) -> Dict[str, str]:
        pass

    def GetValue(self, remoteId: int, name: str = None) -> str:
        pass

    def GetResults(self, remoteId: int):
        pass
