from Helper import Log, Level
from os.path import realpath, exists
from os import makedirs
import threading
from tempfile import TemporaryDirectory


class Child:
    TEMP_BASE = 'Temp'

    def __init__(self, name: str):
        self.name = name
        self.thread = threading.Thread(
            target=self._runWrapper,
            daemon=True
        )
        self.stopRequested = False
        self.TempFolder = None

    def Broadcast(self, level: Level, msg: str):
        Log.Log(level, f'[{self.name}{self.thread.ident}] {msg}')

    def Log(self, level: Level, msg: str):
        Log.Log(level, msg, logger=self.name)

    def Start(self):
        self.thread.start()

    def RequestStop(self):
        self.stopRequested = True

    def _runWrapper(self):
        basefolder = realpath(self.TEMP_BASE)
        if not exists(basefolder): makedirs(basefolder)
        with TemporaryDirectory(dir=basefolder) as tempFolder:
            self.TempFolder = tempFolder
            Log.OpenLogFile(self.name)
            self.Run()
            Log.CloseLogFile(self.name)

    def Run(self):
        raise NotImplementedError()
