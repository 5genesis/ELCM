from Helper import Level
from typing import Dict
from time import sleep
from .executor_base import ExecutorBase
from Task import Task
from .Tasks.Run import Instantiate, Report, Decommission
from .status import Status
from tempfile import TemporaryDirectory
from math import floor


class Executor(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "Executor", tempFolder)

    def Run(self):
        self.SetStarted()

        Instantiate(self.Log).Start()
        self.AddMessage('Instantiation completed', 10)

        tasks = self.Configuration.RunTasks
        for i, task in zip(range(1, len(tasks) + 1), tasks):
            if self.stopRequested:
                self.LogAndMessage(Level.INFO, "Received stop request, exiting")
                self.Status = Status.Cancelled
                break
            taskInstance: Task = task.Task(self.Log, self.ExpandParams(task.Params))
            self.AddMessage(f'Starting task {taskInstance.name}')
            taskInstance.Start()
            sleep(2)
            self.AddMessage(f'Task {taskInstance.name} finished', int(floor(10 + ((i / len(tasks)) * 80))))
        else:
            self.Status = Status.Finished

        Decommission(self.Log).Start()
        self.AddMessage('Decommision completed', 100)

        self.SetFinished(percent=100)
