from typing import Dict
from .Tasks.PreRun import CheckAvailable, AddExecutionEntry, Instantiate
from .executor_base import ExecutorBase
from tempfile import TemporaryDirectory
from time import sleep


class PreRunner(ExecutorBase):
    def __init__(self, params: Dict, tempFolder: TemporaryDirectory = None):
        super().__init__(params, "PreRunner", tempFolder)

    def Run(self):
        self.SetStarted()

        self.AddMessage("Configuration completed", 30)
        available = False
        while not available:
            result = CheckAvailable(self.Log, self.Id, self.Configuration.Requirements).Start()
            available = result['Available']
            if not available:
                self.AddMessage('Not available')
                sleep(1)

        self.AddMessage('Resources granted', 50)
        AddExecutionEntry(self.Log).Start()
        self.AddMessage('Execution registered', 50)

        result = Instantiate(self.Log, self.TempFolder, self.Configuration.PreRunParams).Start()
        self.Configuration.PostRunParams["SliceId"] = result["SliceId"]
        self.params["SliceId"] = result["SliceId"]  # TODO: Improve inter-executor communication

        self.AddMessage('Instantiation completed', 80)
        self.SetFinished(percent=100)
