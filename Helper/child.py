from Helper import Log, Level
import threading


class Child:
    def __init__(self, name: str):
        self.name = name
        self.thread = threading.Thread(
            target=self._runWrapper,
            daemon=True
        )
        self.stopRequested = False

    def Broadcast(self, level: Level, msg: str):
        Log.Log(level, f'[{self.name}{self.thread.ident}] {msg}')

    def Log(self, level: Level, msg: str):
        Log.Log(level, msg, logger=self.name)

    def Start(self):
        self.thread.start()

    def RequestStop(self):
        self.stopRequested = True

    def _runWrapper(self):
        Log.OpenLogFile(self.name)
        self.Run()
        Log.CloseLogFile(self.name)

    def Run(self):
        raise NotImplementedError()
