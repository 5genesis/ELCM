from collections import deque
from Experiment import ExperimentRun, ExperimentStatus
from typing import Deque, Optional, List, Dict
from Helper import Log
from .status import Status


class ExecutionQueue:
    queue: Deque[ExperimentRun] = deque()

    @classmethod
    def Find(cls, executionId) -> Optional[ExperimentRun]:
        needles = [e for e in cls.queue if e.Id == executionId]
        return needles[0] if needles else None

    @classmethod
    def Create(cls, params: Dict) -> ExperimentRun:
        executionId = Status.NextId()
        execution = ExperimentRun(executionId, params)
        cls.queue.appendleft(execution)
        Log.I(f'Created Execution {execution.Id}')
        return execution

    @classmethod
    def Delete(cls, executionId):
        execution = cls.Find(executionId)
        if execution is not None:
            execution.Save()
            cls.queue.remove(execution)

    @classmethod
    def Cancel(cls, executionId: int):
        execution = cls.Find(executionId)
        if execution is not None:
            Log.I(f'Cancelling execution {execution.Id}')
            execution.Cancel()
        else:
            Log.W(f'Cannot cancel execution {executionId}: Not found')

    @classmethod
    def Retrieve(cls, status: Optional[ExperimentStatus] = None) -> List[ExperimentRun]:
        if status is None:
            return list(cls.queue)
        else:
            return [e for e in cls.queue if e.CoarseStatus == status]

    @classmethod
    def UpdateAll(cls):
        executions = cls.Retrieve()
        Log.D(f"UpdateAll: {(', '.join(str(e) for e in executions))}")
        for execution in reversed(executions):  # Reversed to give priority to older executions (for resources)
            Log.D(f"Update Execution: {execution.Id}")
            try:
                if execution.Active:
                    pre = execution.CoarseStatus
                    Log.I(f'Advancing Execution {execution.Id}')
                    execution.Advance()
                    Log.D(f'{execution.Id}: {pre.name} -> {execution.CoarseStatus.name}')
                else:
                    Log.I(f'Removing Execution {execution.Id} from queue (status: {execution.CoarseStatus.name})')
                    cls.Delete(execution.Id)
            except Exception as e:
                Log.C(f"Exeption while updating execution {execution.Id}: {e}")
