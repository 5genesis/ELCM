from Task import Task
from Settings import EvolvedConfig
from Helper import Level


class JenkinsBase(Task):
    def __init__(self, name, parent, params, logMethod):
        super().__init__(name, parent, params, logMethod, None)
        self.config = EvolvedConfig().JenkinsApi

    def Run(self):
        raise NotImplementedError


class JenkinsBuild(JenkinsBase):
    def __init__(self, logMethod, parent, params):
        super().__init__("Jenkins Build", parent, params, logMethod)
        self.paramRules = {}

    def Run(self):
        pass


class JenkinsStatus(JenkinsBase):
    def __init__(self, logMethod, parent, params):
        super().__init__("Jenkins Status", parent, params, logMethod)
        self.paramRules = {}

    def Run(self):
        pass
