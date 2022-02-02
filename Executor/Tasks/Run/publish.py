from Task import Task


class Publish(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Publish", parent, params, logMethod, None)

    def Run(self):
        for key, value in self.params.items():
            self.Publish(key, value)
