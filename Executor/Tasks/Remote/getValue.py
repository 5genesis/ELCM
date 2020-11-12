from Task import Task
from Helper import Level
from time import sleep


class GetValue(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Get Value", parent, params, logMethod, None)

    def Run(self):
        timeout = self.params.get('Timeout', 30)
        valueName = self.params.get('Value', None)
        publishName = self.params.get('PublishName', valueName)

        if valueName is None:
            self.Log(Level.ERROR, "'Value' not defined, please review the Task configuration.")
            return

        value = None
        while value is None:
            self.Log(Level.DEBUG, f"Trying to retrieve '{valueName}' value from remote. Timeout in {timeout} seconds.")
            value = self.parent.RemoteApi.GetValue(self.parent.RemoteId, valueName)
            if value is None:
                if timeout <= 0: break
                sleep(5)
                timeout -= 5

        if value is not None:
            self.Log(Level.INFO, f"Value received ({valueName}={value}).")
            self.Publish(publishName, value)
        else:
            raise RuntimeError(f"Timeout reached while waiting for remote remote value '{valueName}'.")