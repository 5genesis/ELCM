from Task import Task
from Settings import EvolvedConfig
from Interfaces import Evolved5gJenkinsApi
from Helper import Level


class JenkinsBase(Task):
    def __init__(self, name, parent, params, logMethod):
        super().__init__(name, parent, params, logMethod, None)
        self.config = EvolvedConfig().JenkinsApi
        self.client = None

    def Run(self):
        try:
            self.client = self.getApiClient()
        except Exception as e:
            self.Log(Level.Error, f"Unable to create Jenkins API client: {e}")
            self.client = None

    def getApiClient(self) -> Evolved5gJenkinsApi:
        if not self.config.Enabled:
            raise RuntimeError(f"Trying to run {self.name} Task while Jenkins API is not enabled")

        return Evolved5gJenkinsApi(self.config.Host, self.config.Port,
                                   self.config.User, self.config.Password)


class JenkinsBuild(JenkinsBase):
    def __init__(self, logMethod, parent, params):
        super().__init__("Jenkins Build", parent, params, logMethod)
        self.paramRules = {}

    def Run(self):
        super().Run()
        if self.client is None: return


class JenkinsStatus(JenkinsBase):
    def __init__(self, logMethod, parent, params):
        super().__init__("Jenkins Status", parent, params, logMethod)
        self.paramRules = {}

    def Run(self):
        super().Run()
        if self.client is None: return
