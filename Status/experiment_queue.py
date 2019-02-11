from collections import deque
from Experiment import Experiment, ExperimentStatus
from typing import Deque, Optional, List
from Helper import Log


class ExperimentQueue:
    queue: Deque[Experiment] = deque()

    @classmethod
    def Find(cls, experimentId) -> Optional[Experiment]:
        needles = [e for e in cls.queue if e.Id == experimentId]
        return needles[0] if needles else None

    @classmethod
    def Create(cls, experimentId) -> Experiment:
        experiment = Experiment(experimentId)
        cls.queue.appendleft(experiment)
        return experiment

    @classmethod
    def Delete(cls, experimentId):
        experiment = cls.Find(experimentId)
        if experiment is not None: cls.queue.remove(experiment)

    @classmethod
    def Cancel(cls, experimentId: int):
        experiment = cls.Find(experimentId)
        experiment.Cancel()

    @classmethod
    def Retrieve(cls, status: Optional[ExperimentStatus] = None) -> List[Experiment]:
        if status is None:
            return list(cls.queue)
        else:
            return [e for e in cls.queue if e.CoarseStatus == status]

    @classmethod
    def UpdateAll(cls):
        experiments = cls.Retrieve()
        Log.D(f'UpdateAll: {experiments}')
        for experiment in experiments:
            Log.D(f'Advancing Experiment {experiment.Id}')
            experiment.Advance()
