from Helper import Serialize
from Executor import Executor
from .experiment_run import CoarseStatus


class Tombstone:
    def __init__(self, id: str):
        path = Serialize.Path('Execution', id)
        data = Serialize.Load(path)
        self.Id, self.Cancelled, status = Serialize.Unroll(data, 'Id', 'Cancelled', 'CoarseStatus')
        self.Params = {'Id': self.Id, 'Deserialized': True}
        self.CoarseStatus = CoarseStatus[status]
        self.PreRunner = Executor.Load('PreRunner', str(self.Id))
        self.Executor = Executor.Load('Executor', str(self.Id))
        self.PostRunner = Executor.Load('PostRunner', str(self.Id))
        self.Created = Serialize.StringToDate(data['Created'])
        self.JsonDescriptor = data.get('JsonDescriptor', {})
        self.Milestones = data.get('Milestones', [])

