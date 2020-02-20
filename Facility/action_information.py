from sys import maxsize
from typing import Mapping, Dict
from Helper import Log
from typing import List


class ActionInformation:
    def __init__(self):
        self.Order = maxsize  # Default to the lowest order
        self.TaskName = ''
        self.Config = {}
        self.Requirements: List[str] = []

    @classmethod
    def FromMapping(cls, data: Mapping):
        res = ActionInformation()
        try:
            res.Order = data['Order']
            res.TaskName = data['Task']
            res.Config = data['Config']
            res.Requirements = data.get('Requirements', [])
            return res
        except KeyError as e:
            Log.E(f'Facility: Key not found on action information: {e} (Data="{data}")')
            return None

    def __str__(self):
        return f'ActionInformation [Order: {self.Order}; Task: {self.TaskName}; Config: {self.Config}]'

    @staticmethod
    def DummyAction(config: Dict):
        res = ActionInformation()
        res.TaskName = 'Run.Dummy'
        res.Config = config
        return res

    @staticmethod
    def MessageAction(severity: str, message: str):
        res = ActionInformation()
        res.TaskName = 'Run.Message'
        res.Config = {
            'Severity': severity,
            'Message': message
        }
        return res
