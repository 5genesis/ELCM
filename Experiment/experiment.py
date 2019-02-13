from Executor import PreRunner, Executor, PostRunner, ExecutorStatus, ExecutorBase
from typing import Dict, Optional
from enum import Enum, unique
from datetime import datetime
from tempfile import TemporaryDirectory
from Helper import Config, Serialize


@unique
class CoarseStatus(Enum):
    Init, PreRun, Run, PostRun, Finished, Cancelled, Errored = range(7)


class Experiment:
    def __init__(self, id: int, params: Optional[Dict] = None):
        self.Id = id
        self.Params = params if params is not None else {}
        self.Params['Id'] = self.Id
        self.TempFolder = TemporaryDirectory(dir=Config().TempFolder)
        self.PreRunner = PreRunner(self.Params, tempFolder=self.TempFolder)
        self.Executor = Executor(self.Params, tempFolder=self.TempFolder)
        self.PostRunner = PostRunner(self.Params, tempFolder=self.TempFolder)
        self.CoarseStatus = CoarseStatus.Init
        self.Cancelled = False
        self.Created = datetime.utcnow()

    @property
    def Status(self) -> str:
        if self.CoarseStatus == CoarseStatus.PreRun:
            return f'PreRun: {self.PreRunner.Status.name}'
        elif self.CoarseStatus == CoarseStatus.Run:
            return f'Run: {self.Executor.Status.name}'
        elif self.CoarseStatus == CoarseStatus.PostRun:
            return f'PostRun: {self.PostRunner.Status.name}'
        else:
            return self.CoarseStatus.name

    @property
    def Active(self) -> bool:
        return self.CoarseStatus.value < CoarseStatus.Finished.value

    @property
    def CurrentChild(self) -> Optional[ExecutorBase]:
        if self.CoarseStatus == CoarseStatus.PreRun: return self.PreRunner
        if self.CoarseStatus == CoarseStatus.Run: return self.Executor
        if self.CoarseStatus == CoarseStatus.PostRun: return self.PostRunner
        return None

    def Cancel(self):
        current = self.CurrentChild
        if current is not None:
            current.RequestStop()
        self.CoarseStatus = CoarseStatus.Cancelled

    def PreRun(self):
        self.CoarseStatus = CoarseStatus.PreRun
        self.PreRunner.Start()

    def Run(self):
        self.CoarseStatus = CoarseStatus.Run
        self.Executor.Start()

    def PostRun(self):
        self.CoarseStatus = CoarseStatus.PostRun
        self.PostRunner.Start()

    def Advance(self):
        if not self.Active:
            return
        elif self.CoarseStatus == CoarseStatus.Init:
            self.PreRun()
            self.CoarseStatus = CoarseStatus.PreRun
        elif self.CoarseStatus == CoarseStatus.PreRun and self.PreRunner.Finished:
            self.Run()
            self.CoarseStatus = CoarseStatus.Run
        elif self.CoarseStatus == CoarseStatus.Run and self.Executor.Finished:
            self.PostRun()
            self.CoarseStatus = CoarseStatus.PostRun
        elif self.CoarseStatus == CoarseStatus.PostRun and self.PostRunner.Finished:
            self.CoarseStatus = CoarseStatus.Finished
            self.TempFolder.cleanup()

    def Serialize(self) -> Dict:
        data = {
            'Id': self.Id,
            'Created': Serialize.DateToString(self.Created),
            'CoarseStatus': self.CoarseStatus.name,
            'Cancelled': self.Cancelled
        }
        return data

    def Save(self):
        self.PreRunner.Save()
        self.Executor.Save()
        self.PostRunner.Save()
        data = self.Serialize()
        path = Serialize.Path('Experiment', str(self.Id))
        Serialize.Save(data, path)

    @classmethod
    def Load(self, id: str):
        path = Serialize.Path('Experiment', id)
        data = Serialize.Load(path)
        res = Experiment(-1, None)
        res.Id, res.Cancelled, status = Serialize.Unroll(data, 'Id', 'Cancelled', 'CoarseStatus')
        res.Params = {'Id': res.Id, 'Deserialized': True}
        res.CoarseStatus = CoarseStatus[status]
        res.PreRunner = Executor.Load('PreRunner', str(res.Id))
        res.Executor = Executor.Load('Executor', str(res.Id))
        res.PostRunner = Executor.Load('PostRunner', str(res.Id))
        res.Created = Serialize.StringToDate(data['Created'])
        return res

    @classmethod
    def Digest(cls, id: str) -> Dict:
        return Serialize.Load(Serialize.Path('Experiment', id))
