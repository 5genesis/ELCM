from Helper import Child, Level
from typing import Dict
from datetime import datetime
from Helper import Serialize
from .status import Status
from tempfile import TemporaryDirectory


class ExecutorBase(Child):
    def __init__(self, params: Dict, name: str, tempFolder: TemporaryDirectory = None):
        now = datetime.utcnow()
        super().__init__(f"{name}{now.strftime('%y%m%d%H%M%S%f')}", tempFolder)
        self.Tag = name
        self.params = params
        self.Id = params['Id']
        self.Created = now
        self.Started = None
        self.Finished = None
        self.Status = Status.Init
        self.Messages = []
        self.PerCent = 0
        self.AddMessage("Init")

    def AddMessage(self, msg: str, percent: int = None):
        if percent is not None: self.PerCent = percent
        self.Messages.append(f'[{self.PerCent}%] {msg}')

    @property
    def LastMessage(self):
        return self.Messages[-1]

    def LogAndMessage(self, level: Level, msg: str, percent: int = None):
        self.Log(level, msg)
        self.AddMessage(msg, percent)

    def SetStarted(self):
        self.LogAndMessage(Level.INFO, "Started")
        self.Started = datetime.utcnow()
        self.Status = Status.Running

    def SetFinished(self, status=Status.Finished, percent: int = None):
        self.Finished = datetime.utcnow()
        if self.Status.value < Status.Cancelled.value:
            self.Status = status
        self.LogAndMessage(Level.INFO, f"Finished (status: {self.Status.name})", percent)

    def Serialize(self) -> Dict:
        data = {
            'Id': self.Id,
            'Name': self.name,
            'Tag': self.Tag,
            'Created': Serialize.DateToString(self.Created),
            'Started': Serialize.DateToString(self.Started),
            'Finished': Serialize.DateToString(self.Finished),
            'HasStarted': self.hasStarted,
            'HasFinished': self.hasFinished,
            'Status': self.Status.name,
            'Log': self.LogFile,
            'Messages': self.Messages,
            'PerCent': self.PerCent
        }
        return data

    def Save(self):
        data = self.Serialize()
        path = Serialize.Path(self.Tag, str(self.Id))
        Serialize.Save(data, path)

    @classmethod
    def Load(cls, tag: str, id: str):
        path = Serialize.Path(tag, id)
        data = Serialize.Load(path)
        tag = data['Tag']
        params = {'Id': int(id), 'Deserialized': True}
        if tag == 'PreRunner':
            from .pre_runner import PreRunner
            res = PreRunner(params)
        elif tag == 'Executor':
            from .executor import Executor
            res = Executor(params)
        else:
            from .post_runner import PostRunner
            res = PostRunner(params)
        res.Id, res.Name, res.LogFile, res.Tag, res.hasStarted, res.hasFinished, res.Messages, res.PerCent = \
            Serialize.Unroll(data, 'Id', 'Name', 'Log', 'Tag', 'HasStarted', 'HasFinished', 'Messages', 'PerCent')
        res.Created = Serialize.StringToDate(data['Created'])
        res.Started = Serialize.StringToDate(data['Started'])
        res.Finished = Serialize.StringToDate(data['Finished'])
        res.Status = Status[data['Status']]

        return res
