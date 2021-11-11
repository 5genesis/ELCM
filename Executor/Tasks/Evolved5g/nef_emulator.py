from Task import Task
from Settings import EvolvedConfig
from Interfaces import Evolved5gNefEmulator, Loop
from Helper import Level


class NefEmulatorBase(Task):
    def __init__(self, name, parent, params, logMethod):
        super().__init__(name, parent, params, logMethod, None)
        self.config = EvolvedConfig().NefEmulator
        self.client = None

    def Run(self):
        try:
            self.client = self.getApiClient()
        except Exception as e:
            self.Log(Level.Error, f"Unable to create NEF Emulator client: {e}")
            self.client = None

    def getApiClient(self) -> Evolved5gNefEmulator:
        if not self.config.Enabled:
            raise RuntimeError(f"Trying to run {self.name} Task while NEF Emulator is not enabled")

        return Evolved5gNefEmulator(self.config)


class NefLoop(NefEmulatorBase):
    def __init__(self, logMethod, parent, params):
        super().__init__("NEF Emulator Loop", parent, params, logMethod)
        self.paramRules = {
            'Supi': (None, True),
            'Action': ("Start", False),
        }

    def Run(self):
        super().Run()
        if self.client is None: return

        try:
            action = Loop[self.params["Action"].capitalize()]
        except Exception:
            self.Log(Level.ERROR, f"Unrecognized action '{self.params['Action']}'")
            return
        supi = self.params["Supi"]

        self.Log(Level.INFO, f"Trying to {action.name.lower()} loop for supi '{supi}'")

        try:
            msg = self.client.ToggleLoop(supi, action)
            self.Log(Level.INFO, f"Response: {msg}")
        except Exception as e:
            self.Log(Level.ERROR, str(e))
