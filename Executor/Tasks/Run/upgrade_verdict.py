from Task import Task
from Helper import Level
import re


class UpgradeVerdict(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Upgrade Verdict", parent, params, logMethod, None)
        self.paramRules = {
            'Key': (None, True),
            'Pattern': (None, True),
            'VerdictOnMissing': ("NotSet", False),
            'VerdictOnMatch': ("NotSet", False),
            'VerdictOnNoMatch': ("NotSet", False),
        }

    def Run(self):
        onMiss = self.GetVerdictFromName(self.params["VerdictOnMissing"])
        onMatch = self.GetVerdictFromName(self.params["VerdictOnMatch"])
        onNoMatch = self.GetVerdictFromName(self.params["VerdictOnNoMatch"])
        if None in [onMiss, onMatch, onNoMatch]: return

        key = self.params["Key"]
        regex = re.compile(self.params["Pattern"])
        collection = self.parent.Params

        if key not in collection.keys():
            self.Log(Level.WARNING, f"Key '{key}' not found. Setting Verdict to '{onMiss.name}'")
            self.Log(Level.DEBUG, f"Available keys: {list(collection.keys())}")
            self.Verdict = onMiss
        else:
            value = str(collection[key])
            if regex.match(value):
                condition = "matches"
                verdict = onMatch
            else:
                condition = "does not match"
                verdict = onNoMatch

            self.Log(Level.INFO, f"'{key}'='{value}' {condition} pattern. Setting Verdict to '{verdict.name}'")
            self.Verdict = verdict

