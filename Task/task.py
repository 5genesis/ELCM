from typing import Callable, Dict, Optional, Union, Tuple, Any
from Helper import Log, Level
from Settings import Config


class Task:
    def __init__(self, name: str, parent, params: Optional[Dict] = None,
                 logMethod: Optional[Callable] = None,
                 conditionMethod: Optional[Callable] = None):
        from Executor import ExecutorBase, Verdict

        self.name = name
        self.params = {} if params is None else params
        self.paramRules: Dict[str, Tuple[Any, bool]] = {}  # Dict[<ParameterName>: (<Default>, <Mandatory>)]
        self.parent: ExecutorBase = parent
        self.logMethod = Log.Log if logMethod is None else logMethod
        self.condition = conditionMethod
        self.Vault = {}
        self.LogMessages = []
        self.Verdict = Verdict.NotSet

    def Start(self) -> Dict:
        if self.condition is None or self.condition():
            self.Log(Level.INFO, f"[Starting Task '{self.name}']")
            self.Log(Level.DEBUG, f'Params: {self.params}')
            if self.SanitizeParams():
                self.Run()
                self.Log(Level.INFO, f"[Task '{self.name}' finished (verdict: '{self.Verdict.name}')]")
            else:
                message = f"[Task '{self.name}' cancelled due to incorrect parameters ({self.params})]"
                self.Log(Level.ERROR, message)
                raise RuntimeError(message)
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
        self.LogMessages.append(msg)

    def SanitizeParams(self):
        for key, value in self.paramRules.items():
            default, mandatory = value
            if key not in self.params.keys():
                if mandatory:
                    self.Log(Level.ERROR, f"Parameter '{key}' is mandatory but was not configured for the task.")
                    return False
                else:
                    self.params[key] = default
                    self.Log(Level.DEBUG, f"Parameter '{key}' set to default ({str(default)}).")
        return True

    def SetVerdictOnError(self):
        from Executor import Verdict
        verdict = self.params.get('VerdictOnError', None)
        if verdict is None:
            verdict = Config().VerdictOnError
        try:
            self.Verdict = Verdict[verdict]
        except KeyError as e:
            raise RuntimeError(f"Unrecognized Verdict '{verdict}'") from e

    def GetVerdictFromName(self, name: str):
        from Executor import Verdict
        try:
            return Verdict[name]
        except KeyError:
            self.SetVerdictOnError()
            self.Log(Level.ERROR, f"Unrecognized Verdict '{name}'")
            return None
