from enum import Enum, unique


@unique
class Status(Enum):
    Init, Waiting, Running, Cancelled, Errored, Finished = range(6)

    def label(self):
        if self.name == 'Cancelled': return 'label-warning'
        if self.name == 'Errored': return 'label-danger'
        if self.name == 'Finished': return 'label-success'
        return 'label-info'
