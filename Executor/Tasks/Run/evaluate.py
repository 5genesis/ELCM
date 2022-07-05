from Task import Task
from Helper import Level
import re


class Evaluate(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Evaluate", parent, params, logMethod, None)
        self.paramRules = {
            'Key': (None, True),
            'Expression': (None, True)
        }

    def Run(self):
        expression = self.params["Expression"]
        key = self.params["Key"]
        self.Log(Level.INFO, f"Evaluating '{key} = {expression}'")

        try:
            result = eval(expression)
        except Exception as e:
            self.Log(Level.ERROR, f"Exception while evaluating expression '{expression}'")
            raise e

        self.Publish(key, str(result))
