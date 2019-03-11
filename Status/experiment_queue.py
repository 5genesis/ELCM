from collections import deque
from Experiment import ExperimentRun, ExperimentStatus
from typing import Deque, Optional, List, Dict
from Helper import Log
from .status import Status


class ExperimentQueue:
    queue: Deque[ExperimentRun] = deque()

    @classmethod
    def Find(cls, experimentId) -> Optional[ExperimentRun]:
        needles = [e for e in cls.queue if e.Id == experimentId]
        return needles[0] if needles else None

    @classmethod
    def Create(cls, params: Dict) -> ExperimentRun:
        experimentId = Status.NextId()
        experiment = ExperimentRun(experimentId, params)
        cls.queue.appendleft(experiment)
        Log.I(f'Created Experiment {experiment.Id}')
        return experiment

    @classmethod
    def Delete(cls, experimentId):
        experiment = cls.Find(experimentId)
        if experiment is not None:
            experiment.Save()
            cls.queue.remove(experiment)

    @classmethod
    def Cancel(cls, experimentId: int):
        experiment = cls.Find(experimentId)
        experiment.Cancel()

    @classmethod
    def Retrieve(cls, status: Optional[ExperimentStatus] = None) -> List[ExperimentRun]:
        if status is None:
            return list(cls.queue)
        else:
            return [e for e in cls.queue if e.CoarseStatus == status]

    @classmethod
    def UpdateAll(cls):
        experiments = cls.Retrieve()
        for experiment in experiments:
            if experiment.Active:
                pre = experiment.CoarseStatus
                Log.I(f'Advancing Experiment {experiment.Id}')
                experiment.Advance()
                Log.D(f'{experiment.Id}: {pre.name} -> {experiment.CoarseStatus.name}')
            else:
                Log.I(f'Removing Experiment {experiment.Id} from queue (status: {experiment.CoarseStatus.name})')
                cls.Delete(experiment.Id)
