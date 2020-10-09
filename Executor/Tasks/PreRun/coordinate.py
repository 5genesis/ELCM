from Task import Task
from Helper import Level, Config


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
                    remoteApi = None  # TODO: Implement API
                    self.parent.RemoteApi = remoteApi
                    # TODO: Wait for remote experiment ID
                else:
                    raise RuntimeError(f"Unknown remote '{remote}'.")
            else:
                raise RuntimeError("Unable to run distributed experiment while East/West interface is disabled.")
        else:
            self.Log(Level.INFO, 'Remote not set, skipping coordination.')
