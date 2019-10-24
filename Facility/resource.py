from typing import Dict, Optional


class Resource:
    def __init__(self, data: Dict):
        self.Id = data["Id"]
        self.Name = data["Name"]
        self.Icon = data.get("Icon", "fa-cash-register")
        self.Owner: Optional["ExperimentRun"] = None

    @property
    def Locked(self):
        return self.Owner is None
