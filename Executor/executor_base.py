from Helper import Child, Level
from typing import Dict
from datetime import datetime
from .api import Api
from Helper import Serialize
from .status import Status


class ExecutorBase(Child):
    api = None

    def __init__(self, params: Dict, name: str):
        now = datetime.utcnow()
        super().__init__(f"{name}{now.strftime('%y%m%d%H%M%S%f')}")
        self.Tag = name
        self.params = params
        self.Id = params['Id']
        self.Created = now
        self.Started = None
        self.Finished = None
        self.Status = Status.Init

        if self.api is None: self.api=Api('127.0.0.1', '5000')

    def Save(self):
        data = {
            'Id': self.Id,
            'Name': self.name,
            'Tag': self.Tag,
            'Created': Serialize.DateToString(self.Created),
            'Started': Serialize.DateToString(self.Started),
            'Finished': Serialize.DateToString(self.Finished),
            'Status': self.Status.name,
            'Log': self.LogFile,
        }
        path = Serialize.Path('Executor', str(self.Id))
        Serialize.Save(data, path)

    @classmethod
    def Load(cls, id: str):
        path = Serialize.Path('Executor', id)
        data = Serialize.Load(path)
        tag = data['Tag']
        params = {'Id': 'Deserialized', 'Deserialized': True}
        if tag == 'PreRunner':
            from .pre_runner import PreRunner
            res = PreRunner(params)
        elif tag == 'Executor':
            from .executor import Executor
            res = Executor(params)
        else:
            from .post_runner import PostRunner
            res = PostRunner(params)
        res.Id, res.Name, res.Log, res.Tag = Serialize.Unroll(data, 'Id', 'Name', 'Log', 'Tag')
        res.Created = Serialize.StringToDate(data['Created'])
        res.Started = Serialize.StringToDate(data['Started'])
        res.Finished = Serialize.StringToDate(data['Finished'])
        res.Status = Status[data['Status']]
        return res
