from Helper import Serialize
from typing import Dict, Tuple, List, Optional
from enum import Enum, unique
from datetime import datetime, timezone


@unique
class ExperimentType(Enum):
    Error = 0
    Standard = 1
    Custom = 2
    MONROE = 3
    Distributed = 4


class ExperimentDescriptor:
    def __init__(self, data: Dict):
        time = datetime.now(timezone.utc).strftime("%y%m%d%H%M%S")
        self.Valid, self.Missing = self.validate(data)
        self._data = data
        if self.Valid:
            self.Type = ExperimentType[data['ExperimentType']]
            self.Identifier = f"{time}{self.Type.name}:{(','.join(self.TestCases))}-{(','.join(self.UEs))}"
        else:
            self.Type = ExperimentType.Error
            self.Identifier = time

    @staticmethod
    def validate(data: Dict) -> Tuple[bool, List[str]]:
        keys = ['Version', 'ExperimentType', 'TestCases', 'UEs', 'Slice', 'NSs',
                'ExclusiveExecution', 'Scenario', 'Automated', 'ReservationTime',
                'Application', 'Parameters', 'Remote', 'Extra']
        return Serialize.CheckKeys(data, *keys)

    @property
    def Json(self) -> Dict:
        return self._data

    @property
    def Version(self) -> str:
        return self._data['Version']

    @property
    def TestCases(self) -> List[str]:
        return self._data['TestCases']

    @property
    def UEs(self) -> List[str]:
        return self._data['UEs']

    @property
    def Slice(self) -> str:
        return self._data['Slice']

    @property
    def NetworkServices(self) -> List[Tuple[str, str]]:
        return self._data['NSs']

    @property
    def Exclusive(self) -> bool:
        return self._data['ExclusiveExecution']

    @property
    def Scenario(self) -> str:
        return self._data['Scenario']

    @property
    def Automated(self) -> bool:
        return self._data['Automated']

    @property
    def Duration(self) -> int:
        return self._data['ReservationTime']

    @property
    def Application(self) -> str:
        return self._data['Application']

    @property
    def Parameters(self) -> Dict[str, object]:
        return self._data['Parameters']

    @property
    def Extra(self) -> Dict[str, object]:
        return self._data['Extra']

    @property
    def Remote(self) -> Optional[str]:
        return self._data['Remote']

    @property
    def RemoteDescriptor(self) -> Optional[Dict]:
        return self._data.get("RemoteDescriptor", None)

    @property
    def ValidityCheck(self) -> Tuple[bool, List[str]]:
        reasons = []
        if not self.Valid:
            reasons.append(f'Missing data: {self.Missing}')

        return len(reasons) == 0, reasons
