from typing import Dict
from .Tasks.PreRun import CheckResources, Instantiate
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
            result = CheckResources(self.Log, self.ExecutionId, self.Configuration.Requirements,
                                    self.Configuration.NetworkServices, self).Start()
            available = result['Available']
            if not available:
                self.AddMessage('Not available')
                sleep(10)

        Instantiate(self.Log, self.TempFolder, self, self.Configuration.NetworkServices).Start()
        self.AddMessage('Instantiation completed', 80)

        self.SetFinished(percent=100)
