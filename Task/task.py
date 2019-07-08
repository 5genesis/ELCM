from typing import Callable, Dict, Optional, Union
from Helper import Log, Level


class Task:
    def __init__(self, name: str, params: Optional[Dict] = None,
                 logMethod: Optional[Callable] = None,
                 conditionMethod: Optional[Callable] = None):
        self.name = name
        self.params = {} if params is None else params
        self.logMethod = Log.Log if logMethod is None else logMethod
        self.condition = conditionMethod

    def Start(self) -> Dict:
        if self.condition is None or self.condition():
            self.Log(Level.INFO, f'[Starting Task {self.name}]')
            self.Log(Level.DEBUG, f'Params: {self.params}')
            self.Run()
            self.Log(Level.INFO, f'[Task {self.name} finished]')
            self.Log(Level.DEBUG, f'Params: {self.params}')
        else:
            self.Log(Level.INFO, f'[Task {self.name} not started (condition false)]')
        return self.params

    def Run(self) -> None:
        raise NotImplementedError

    def Log(self, level: Union[Level, str], msg: str):
        self.logMethod(level, msg)
