from Helper import Child, Level
from typing import Dict
from os.path import realpath, exists
from os import makedirs
from time import sleep
from tempfile import TemporaryDirectory
from datetime import datetime


class Executor(Child):
    TEMP_FOLDER = 'ExecutorTempFiles'

    def __init__(self, params: Dict):
        super().__init__(f"Executor{datetime.now().strftime('%y%m%d%H%M%S%f')}")
        self.params = params
        self.basefolder = realpath(self.TEMP_FOLDER)
        if not exists(self.basefolder): makedirs(self.basefolder)

    def Run(self):
        self.Broadcast(Level.INFO, "ALIVE!!")
        self.Log(Level.DEBUG, "Starting")

        with TemporaryDirectory(dir=self.basefolder, prefix='Exec_') as tempFolder:
            self.Broadcast(Level.INFO, f"folder created {tempFolder}")
            self.Log(Level.DEBUG, "processing")
            sleep(10)
            self.Broadcast(Level.INFO, "wololo")

        sleep(1)
        self.Broadcast(Level.INFO, "out!")
        self.Log(Level.DEBUG, "out")
