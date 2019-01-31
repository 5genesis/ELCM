from Helper import Log, Level
from os.path import realpath, exists
from os import makedirs
import threading
from tempfile import TemporaryDirectory
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass


@dataclass
class LogInfo:
    Log: List[Tuple[str, str]] = None
    Count: Dict[str, int] = None

    def __init__(self):
        self.Log = []
        self.Count = {"Debug": 0, "Info": 0, "Warning": 0, "Error": 0, "Critical": 0}

    @staticmethod
    def FromLog(log: List[str]):
        def _inferLevel(line:str) -> str:
            if ' - CRITICAL - ' in line: return 'Critical'
            if ' - ERROR - ' in line: return 'Error'
            if ' - WARNING - ' in line: return 'Warning'
            if ' - INFO - ' in line: return 'Info'
            return 'Debug'

        res = LogInfo()
        for line in log:
            level = _inferLevel(line)
            res.Count[level] += 1
            res.Log.append((level, line))
        return res


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
        self.LogFile = None

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
            self.LogFile = Log.OpenLogFile(self.name)
            self.Log(Level.DEBUG, f'[Using temporal folder: {tempFolder}]')
            self.Run()
            Log.CloseLogFile(self.name)

    def RetrieveLog(self, tail: Optional[int] = None) -> List[str]:
        res = []
        with open(self.LogFile, 'r', encoding='utf-8') as file:
            for l in file: res.append(l)
        if tail is not None and tail < len(res):
            start = len(res) - tail
            return res[start:len(res)]
        return res

    def RetrieveLogInfo(self, tail: Optional[int] = None) -> LogInfo:
        log = self.RetrieveLog(tail)
        return LogInfo.FromLog(log)

    def Run(self):
        raise NotImplementedError()
