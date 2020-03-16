from Task import Task
from Helper import Level
from Interfaces import Management


class Decommission(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Decommission", parent, params, logMethod, None)

    def Run(self):
        self.Log(Level.INFO, 'Decommision started')
        hasNsd = self.params['HasNsd']
        sliceId = self.params.get('SliceId', None)

        if hasNsd:
            if sliceId is not None and sliceId != "None":
                self.Log(Level.INFO, f"Deleting slice {sliceId}")
                response = Management.SliceManager().Delete(sliceId)
                self.Log(Level.DEBUG, f"  Response: '{response}'")
            else:
                self.Log(Level.WARNING, 'Slice identifier is None.')
        else:
            self.Log(Level.INFO, 'Slice not instantiated.')

        self.Log(Level.INFO, 'Decommision completed')
