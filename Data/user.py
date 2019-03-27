from Helper import Serialize
from typing import Dict, Tuple, List


class User:
    def __init__(self, data: Dict):
        self.Valid, self.Missing = self.validate(data)
        self._data = data

    @staticmethod
    def validate(data: Dict) -> Tuple[bool, List[str]]:
        keys = ['Id', 'UserName', 'Email', 'Organization']
        return Serialize.CheckKeys(data, *keys)

    @property
    def Id(self) -> int:
        return self._data['Id']

    @property
    def Name(self) -> str:
        return self._data['UserName']

    @property
    def Email(self) -> str:
        return self._data['Email']

    @property
    def Organization(self) -> str:
        return self._data['Organization']
