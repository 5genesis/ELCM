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


class JenkinsJob(JenkinsBase):
    def __init__(self, logMethod, parent, params):
        super().__init__("Jenkins Job", parent, params, logMethod)
        self.paramRules = {
            'Instance': (None, True),
            'Job': (None, True),
            'GitUrl': (None, True),
            'GitBranch': (None, True),
            'Version': ('1.0', False),
            'PublishKey': ('JenkinsJobId', False),
        }

    def Run(self):
        super().Run()
        if self.client is None: return

        instance = self.params["Instance"]
        job = self.params["Job"]
        url = self.params["GitUrl"]
        branch = self.params["GitBranch"]
        version = self.params["Version"]

        self.Log(Level.DEBUG,
                 f"Trying to trigger job '{job}' on instance '{instance}' ({url}|{branch}|{version})")

        try:
            jobId = self.client.TriggerJob(instance, job, url, branch, version)
            self.Log(Level.INFO, f"Triggered '{job}'. Received Job Id: {jobId}")
            self.Publish(self.params["PublishKey"], jobId)
        except Exception as e:
            self.Log(Level.ERROR, f"Unable to trigger job: {e}")
            self.MaybeSetErrorVerdict()


class JenkinsStatus(JenkinsBase):
    def __init__(self, logMethod, parent, params):
        super().__init__("Jenkins Status", parent, params, logMethod)
        self.paramRules = {
            'JobId': (None, True),
            'PublishKey': ('JenkinsJobStatus', False),
        }

    def Run(self):
        super().Run()
        if self.client is None: return

        jobId = self.params['JobId']

        try:
            status, message = self.client.CheckJob(jobId)
            message = message if message is not None else "<No details>"
            self.Log(Level.INFO, f"Status of job '{jobId}': {status} ('{message}')")
            self.Publish(self.params["PublishKey"], status)
        except Exception as e:
            self.Log(Level.ERROR, f"Unable to check job '{jobId}' status: {e}")
            self.MaybeSetErrorVerdict()
