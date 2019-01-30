from collections import deque
from Executor import Executor, ExecutorStatus
from typing import Deque, Optional, List


class ExperimentQueue:
    queue: Deque[Executor] = deque()

    @classmethod
    def Find(cls, executorId) -> Optional[Executor]:
        needles = [e for e in cls.queue if e.Id == executorId]
        return needles[0] if needles else None

    @classmethod
    def CreateExecutor(cls, executorId) -> Executor:
        executor = Executor(params={'Id': executorId})
        cls.queue.appendleft(executor)
        return executor

    @classmethod
    def DeleteExecutor(cls, executorId: int):
        executor = cls.Find(executorId)
        if executor is not None: cls.queue.remove(executor)

    @classmethod
    def CancelExecutor(cls, executorId: int):
        executor = cls.Find(executorId)
        if executor is not None: executor.RequestStop()

    @classmethod
    def Retrieve(cls, status: Optional[ExecutorStatus] = None) -> List[Executor]:
        if status is None:
            return list(cls.queue)
        else:
            return [e for e in list(cls.queue) if e.Status == status]
