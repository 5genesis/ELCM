from Task import Task
from Helper import Level, Config
from time import sleep
from Interfaces import RemoteApi


class Coordinate(Task):
    def __init__(self, logMethod, parent):
        super().__init__("Coordinate", parent, logMethod, None)

    def Run(self):
        remote = self.parent.Descriptor.Remote
        if remote is not None:
            eastWest = Config().EastWest
            if eastWest.Enabled:
                host, port = eastWest.GetRemote(remote)
                if host is not None:
                    remoteApi = RemoteApi(host, port)
                    self.parent.RemoteApi = remoteApi
                    # TODO: Why are these messages not visible in the logs?
                    self.Log(Level.INFO, 'Remote connection configured. Waiting for remote Execution ID...')

                    timeout = eastWest.Timeout or 120
                    while self.parent.RemoteId is None:
                        if timeout < 0: break
                        self.Log(Level.DEBUG, f'Unavailable. Timeout in {timeout} seconds.')
                        sleep(5)
                        timeout -= 5

                    if self.parent.RemoteId is not None:
                        self.Log(Level.INFO, 'Remote Execution ID received.')
                    else:
                        raise RuntimeError("Timeout reached while waiting for remote Execution ID.")
                else:
                    raise RuntimeError(f"Unknown remote '{remote}'.")
            else:
                raise RuntimeError("Unable to run distributed experiment while East/West interface is disabled.")
        else:
            self.Log(Level.INFO, 'Remote not set, skipping coordination.')
