from typing import Dict, Tuple
from Helper import Serialize


class DashboardPanel:
    def __init__(self, data: Dict):
        self.Measurement, self.Field, self.Order = Serialize.Unroll(data, "Measurement", "Field", "Order")
        self.Size, self.Position = Serialize.Unroll(data, "Size", "Position")
        self.Interval, self.Lines, self.Percentage = Serialize.Unroll(data, "Interval", "Lines", "Percentage")


    def AsDict(self):
        return {
            "Measurement": self.Measurement, "Field": self.Field, "Order": self.Order,
            "Size": self.Size, "Position": self.Position,
            "Interval": self.Interval, "Lines": self.Lines, "Percentage": self.Percentage
        }

    def Generate(self, panelId: int, experimentId: int) -> Dict:
        res = self.panelBase(panelId)
        res["targets"] = [self.getTarget(experimentId)]
        return res

    def panelBase(self, panelId: int) -> Dict:
        return {
            "id": panelId,
            "title": f"{self.Measurement}: {self.Field}",
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
            "measurement": self.Measurement,
            "orderByTime": self.Order,
            "policy": "default",
            "rawQuery": False,
            "refId": "A",
            "resultFormat": "time_series",
            "groupBy": [
                {"params": [f"{'$__interval' if self.Interval is None else self.Interval}"], "type": "time"},
                {"params": ["null"], "type": "fill"}
            ],
            "select": [
                [
                    {"params": [self.Field], "type": "field"},
                    {"params": [], "type": "mean"}
                ]
            ],
            "tags": [{"key": "ExperimentId", "operator": "=", "value": str(experimentId)}]
        }
