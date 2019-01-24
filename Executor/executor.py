from Helper import Child, Level
from typing import Dict
from os.path import realpath, exists
from os import makedirs
from time import sleep
from tempfile import TemporaryDirectory


class Executor(Child):
    TEMP_FOLDER = 'ExecutorTempFiles'

    def __init__(self, params: Dict):
        super().__init__("Executor")
        self.params = params
        self.basefolder = realpath(self.TEMP_FOLDER)
        if not exists(self.basefolder): makedirs(self.basefolder)

    def Run(self):
        self.Say(Level.INFO, "ALIVE!!")

        with TemporaryDirectory(dir=self.basefolder, prefix='Exec_') as tempFolder:
            self.Say(Level.INFO, f"folder created {tempFolder}")
            sleep(10)
            self.Say(Level.INFO, "wololo")

        sleep(1)
        self.Say(Level.INFO, "out!")
