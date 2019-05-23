from typing import Dict, Tuple
from Helper import Serialize


class DashboardPanel:
    def __init__(self, data: Dict):
        self.Name, self.Order = Serialize.Unroll(data, "Name", "Order")
        self.Size, self.Position = Serialize.Unroll(data, "Size", "Position")
        self.Lines, self.Percentage = Serialize.Unroll(data, "Lines", "Percentage")

    def AsDict(self):
        return {
            "Name": self.Name, "Order": self.Order,
            "Size": self.Size, "Position": self.Position,
            "Lines": self.Lines, "Percentage": self.Percentage
        }

    def Generate(self, panelId: int, experimentId: int) -> Dict:
        res = self.panelBase(panelId)
        res["targets"] = [self.getTarget(experimentId)]
        return res

    def panelBase(self, panelId: int) -> Dict:
        return {
            "id": panelId,
            "title": self.Name,
            "aliasColors": {},
            "bars": not self.Lines,
            "dashLength": 10,
            "dashes": False,
            "fill": 1,
            "gridPos": {
                "h": self.Size[0], "w": self.Size[1],
                "x": self.Position[0], "y": self.Position[1]
            },
            "legend": {
                "avg": False, "current": False, "max": False, "min": False,
                "show": True, "total": False, "values": False
            },
            "lines": self.Lines,
            "linewidth": 1,
            "nullPointMode": "null",
            "percentage": self.Percentage,
            "pointradius": 5,
            "points": False,
            "renderer": "flot",
            "seriesOverrides": [],
            "spaceLength": 10,
            "stack": False,
            "steppedLine": False,
            "thresholds": [],
            "timeFrom": None,
            "timeRegions": [],
            "timeShift": None,
            "tooltip": {"shared": True, "sort": 0, "value_type": "individual"},
            "type": "graph",
            "xaxis": {
                "buckets": None, "mode": "time", "name": None,
                "show": True, "values": []
            },
            "yaxes": [
                {
                    "format": "short", "label": None, "logBase": 1,
                    "max": None, "min": None, "show": True
                },
                {
                    "format": "short", "label": None, "logBase": 1,
                    "max": None, "min": None, "show": True
                }
            ],
            "yaxis": {"align": False, "alignLevel": None}
        }

    def getTarget(self, experimentId: int) -> Dict:
        return {
            "hide": False,
            "measurement": self.Name,
            "orderByTime": self.Order,
            "policy": "default",
            "rawQuery": False,
            "refId": "A",
            "resultFormat": "time_series",
            "groupBy": [
                {"params": ["$__interval"], "type": "time"},
                {"params": ["null"], "type": "fill"}
            ],
            "select": [
                [
                    {"params": [self.Name], "type": "field"},
                    {"params": [], "type": "mean"}
                ]
            ],
            "tags": [{"key": "ExperimentId", "operator": "=", "value": str(experimentId)}]
        }
