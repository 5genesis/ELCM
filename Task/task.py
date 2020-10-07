from typing import Callable, Dict, Optional, Union
from Helper import Log, Level


class Task:
    def __init__(self, name: str, parent, params: Optional[Dict] = None,
                 logMethod: Optional[Callable] = None,
                 conditionMethod: Optional[Callable] = None):
        from Executor import ExecutorBase

        self.name = name
        self.params = {} if params is None else params
        self.parent: ExecutorBase = parent
        self.logMethod = Log.Log if logMethod is None else logMethod
        self.condition = conditionMethod
        self.Vault = {}

    def Start(self) -> Dict:
        if self.condition is None or self.condition():
            self.Log(Level.INFO, f"[Starting Task '{self.name}']")
            self.Log(Level.DEBUG, f'Params: {self.params}')
            self.Run()
            self.Log(Level.INFO, f"[Task '{self.name}' finished]")
            self.Log(Level.DEBUG, f'Params: {self.params}')
        else:
            self.Log(Level.INFO, f"[Task '{self.name}' not started (condition false)]")
        return self.params

    def Publish(self, key: str, value: object):
        self.Log(Level.DEBUG, f'Published value "{value}" under key "{key}"')
        self.Vault[key] = value

    def Run(self) -> None:
        raise NotImplementedError

    def Log(self, level: Union[Level, str], msg: str):
        self.logMethod(level, msg)
