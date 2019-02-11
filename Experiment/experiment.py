from Executor import PreRunner, Executor, PostRunner, ExecutorStatus, ExecutorBase
from typing import Dict, Optional
from enum import Enum, unique


@unique
class CoarseStatus(Enum):
    Init, PreRun, Run, PostRun, Finished, Cancelled = range(6)


class Experiment:
    def __init__(self, id: int, params: Optional[Dict] = None):
        self.Id = id
        self.Params = params if params is not None else {}
        self.Params['Id'] = self.Id
        self.PreRunner = PreRunner(self.Params)
        self.Executor = Executor(self.Params)
        self.PostRunner = PostRunner(self.Params)
        self.CoarseStatus = CoarseStatus.Init
        self.Cancelled = False
        self.stepFinished = False

    @property
    def Status(self) -> str:
        if self.CoarseStatus == CoarseStatus.PreRun:
            return f'PreRun: {self.PreRunner.Status}'
        elif self.CoarseStatus == CoarseStatus.Run:
            return f'Run: {self.Executor.Status}'
        elif self.CoarseStatus == CoarseStatus.PostRun:
            return f'PostRun: {self.PostRunner.Status}'
        else:
            return self.CoarseStatus.name

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
        if self.CoarseStatus == CoarseStatus.Cancelled:
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
