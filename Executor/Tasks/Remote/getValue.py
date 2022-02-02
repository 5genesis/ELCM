from .base_remote_task import BaseRemoteTask
from Helper import Level
from time import sleep


class GetValue(BaseRemoteTask):
    def __init__(self, logMethod, parent, params):
        super().__init__("Get Value", logMethod, parent, params)

    def Run(self):
        valueName = self.params.get('Value', None)
        publishName = self.params.get('PublishName', valueName)

        if valueName is None:
            self.Log(Level.ERROR, "'Value' not defined, please review the Task configuration.")
            self.MaybeSetErrorVerdict()
            return

        value = None
        while value is None:
            self.Log(Level.DEBUG,
                     f"Trying to retrieve '{valueName}' value from remote. Timeout in {self.timeout} seconds.")
            value = self.remoteApi.GetValue(self.remoteId, valueName)
            if value is None:
                if self.timeout <= 0:
                    self.MaybeSetErrorVerdict()
                    raise RuntimeError(f"Timeout reached while waiting for remote remote value '{valueName}'.")
                sleep(5)
                self.timeout -= 5

        self.Log(Level.INFO, f"Value received ({valueName}={value}).")
        self.Publish(publishName, value)

