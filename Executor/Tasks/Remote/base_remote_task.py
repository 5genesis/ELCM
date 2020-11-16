from Task import Task
from Helper import Config


TIMEOUT = Config().EastWest.Timeout


class BaseRemoteTask(Task):
    def __init__(self, taskName, logMethod, parent, params):
        super().__init__(taskName, parent, params, logMethod, None)
        self.timeout = self.params.get('Timeout', TIMEOUT)
        self.remoteApi = self.parent.RemoteApi
        self.remoteId = self.parent.RemoteId
