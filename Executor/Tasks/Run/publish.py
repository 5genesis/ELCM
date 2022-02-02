from Task import Task


class Publish(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Publish", parent, params, logMethod, None)

    def Run(self):
        for key, value in self.params.items():
            if key is "VerdictOnError":
                continue  # This key is automatically added to all tasks
            self.Publish(key, value)
