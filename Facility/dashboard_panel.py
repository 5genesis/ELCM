from typing import Dict, Tuple, List
from Helper import Serialize


class DashboardPanel:
    def __init__(self, data: Dict):
        self.Type, self.Name = Serialize.Unroll(data, "Type", "Name")
        self.MinValue, self.MaxValue, self.Gauge = Serialize.Unroll(data, "MinValue", "MaxValue", "Gauge")
        self.Measurement, self.Field = Serialize.Unroll(data, "Measurement", "Field")
        self.Unit, self.UnitLabel = Serialize.Unroll(data, "Unit", "UnitLabel")
        self.Size, self.Position = Serialize.Unroll(data, "Size", "Position")
        self.Interval, self.Lines, self.Percentage = Serialize.Unroll(data, "Interval", "Lines", "Percentage")
        self.Dots, self.Color, self.Thresholds = Serialize.Unroll(data, "Dots", "Color", "Thresholds")

    def AsDict(self):
        return {
            "Type": self.Type, "Name": self.Name,
            "MinValue": self.MinValue, "MaxValue": self.MaxValue, "Gauge": self.Gauge,
            "Measurement": self.Measurement, "Field": self.Field,
            "Unit": self.Unit, "UnitLabel": self.UnitLabel,
            "Size": self.Size, "Position": self.Position,
            "Interval": self.Interval, "Lines": self.Lines, "Percentage": self.Percentage,
            "Dots": self.Dots, "Color": self.Color, "Thresholds": self.Thresholds
        }

    def Generate(self, panelId: int, experimentId: int) -> Dict:
        res = {}
        if self.Type.lower() == "graph":
            res = self.graphPanel(panelId)
        elif self.Type.lower() == "singlestat":
            res = self.singlestatPanel(panelId)
        res["targets"] = [self.getTarget(experimentId)]
        return res

    def singlestatColor(self) -> Dict:
        if self.Gauge:
            colors = self.Color
        else:
            colors = ["#299c46", "rgba(237, 129, 40, 0.89)", "#d44a3a"] if self.Color is None else [self.Color]*3
        return {
            "thresholds": "",
            "colorBackground": False,
            "colorValue": False if (self.Gauge or self.Color is None) else True,
            "colors": colors
        }

    def maybeGauge(self) -> Dict:
        if self.Gauge:
            a, b, c, d = self.Thresholds
            return{
                "gauge": {
                    "show": True, "minValue": a, "maxValue": d, "thresholdMarkers": True, "thresholdLabels": True
                },
                "thresholds": f"{b},{c}"
            }
        else:
            return{
                "gauge": {
                    "show": False, "minValue": 0, "maxValue": 0, "thresholdMarkers": True, "thresholdLabels": True
                }
            }



    def singlestatPanel(self, panelId: int) -> Dict:
        res = {
            "id": panelId,
            "title": f"{self.Measurement}: {self.Field}" if self.Name is None else self.Name,
            "type": "singlestat",
            "links": [],
            "maxDataPoints": 100,
            "interval": None,
            "cacheTimeout": None,
            "format": "none",
            "prefix": "",
            "postfix": "",
            "nullText": None,
            "valueMaps": [{"value": "null", "op": "=", "text": "N/A"}],
            "mappingTypes": [
                {"name": "value to text", "value": 1},
                {"name": "range to text", "value": 2}
            ],
            "rangeMaps": [{"from": "null", "to": "null", "text": "N/A"}],
            "mappingType": 1,
            "nullPointMode": "connected",
            "valueName": "avg",
            "prefixFontSize": "50%",
            "valueFontSize": "80%",
            "postfixFontSize": "50%",
            "sparkline": {
                "show": False,
                "full": False,
                "lineColor": "rgb(31, 120, 193)",
                "fillColor": "rgba(31, 118, 189, 0.18)"
            },
            "gridPos": {
                "h": self.Size[0], "w": self.Size[1],
                "x": self.Position[0], "y": self.Position[1]
            },
            "tableColumn": ""
        }
        res.update(self.singlestatColor())
        res.update(self.maybeGauge())
        return res

    def graphColor(self) -> List[Dict]:
        if self.Color is None:
            return []
        else:
            return [{
                'alias': f'{self.Measurement}.mean',
                'color': self.Color
            }]

    def graphPanel(self, panelId: int) -> Dict:
        return {
            "id": panelId,
            "title": f"{self.Measurement}: {self.Field}" if self.Name is None else self.Name,
            "type": "graph",
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
                "show": False, "total": False, "values": False
            },
            "lines": self.Lines,
            "linewidth": 1,
            "nullPointMode": "connected" if self.Lines else "null",
            "percentage": self.Percentage,
            "pointradius": 5,
            "points": self.Dots if self.Dots is not None else False,
            "renderer": "flot",
            "seriesOverrides": self.graphColor(),
            "spaceLength": 10,
            "stack": False,
            "steppedLine": False,
            "thresholds": [],
            "timeFrom": None,
            "timeRegions": [],
            "timeShift": None,
            "tooltip": {"shared": True, "sort": 0, "value_type": "individual"},
            "xaxis": {
                "buckets": None, "mode": "time", "name": None,
                "show": True, "values": []
            },
            "yaxes": [
                {
                    "format": "short" if self.Unit is None else self.Unit,
                    "label": self.UnitLabel,
                    "logBase": 1,
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
            "orderByTime": "ASC",
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
