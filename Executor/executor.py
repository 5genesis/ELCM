from Helper import Child, Level
from typing import Dict
from datetime import datetime
from .api import Api
from enum import Enum, unique
from .Tasks import Instantiate, Report, Decommission
from Helper import Serialize


@unique
class Status(Enum):
    Init, Waiting, Running, Cancelled, Errored, Finished = range(6)

    def label(self):
        if self.name == 'Cancelled': return 'label-warning'
        if self.name == 'Errored': return 'label-danger'
        if self.name == 'Finished': return 'label-success'
        return 'label-info'


class Executor(Child):
    api = None

    def __init__(self, params: Dict):
        now = datetime.utcnow()
        super().__init__(f"Executor{now.strftime('%y%m%d%H%M%S%f')}")
        self.params = params
        self.Id = params['Id']
        self.Created = now
        self.Started = None
        self.Finished = None
        self.Status = Status.Init

        if self.api is None: self.api=Api('127.0.0.1', '5000')

    def Run(self):
        self.Log(Level.INFO, "Starting")
        self.Started = datetime.utcnow()
        self.api.NotifyStart(self.Id)
        self.Status = Status.Running

        Instantiate(self.Log).Start()

        for _ in range(1, 3):
            if self.stopRequested:
                self.Log(Level.INFO, "Received stop request, exiting")
                self.Status = Status.Cancelled
                break
            Report(self.Log).Start()
        else:
            self.Status = Status.Finished

        Decommission(self.Log).Start()

        self.Finished = datetime.utcnow()
        self.api.NotifyStop(self.Id)
        self.Log(Level.INFO, "Exited")

    def Save(self):
        data = {
            'Id': self.Id,
            'Name': self.name,
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
        res = Executor(params={'Id': 'Temporal', 'Deserialized': True})
        res.Id, res.Name, res.Log = Serialize.Unroll(data, 'Id', 'Name', 'Log')
        res.Created = Serialize.StringToDate(data['Created'])
        res.Started = Serialize.StringToDate(data['Started'])
        res.Finished = Serialize.StringToDate(data['Finished'])
        res.Status = Status[data['Status']]
        return res
