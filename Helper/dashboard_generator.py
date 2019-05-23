from Helper import Log
from REST import RestClient
from Experiment import ExperimentRun
import json
from typing import Dict, Tuple, Optional


class DashboardGenerator(RestClient):
    def __init__(self, host: str, port: int, bearer: str):
        super().__init__(host, port, "/api")
        self.bearer = bearer
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f"Bearer {self.bearer}"
        }

    def Create(self, experiment: ExperimentRun) -> Optional[str]:
        body = json.dumps(self.generateData(experiment))
        Log.D(f"Grafana dashboard data (experiment {experiment.Id}): {body}")
        response = self.httpPost(f"{self.api_url}/dashboards/db", self.headers, body)
        if response.status == 200:
            url = self.responseToJson(response)["url"]
            Log.I(f"Generated Grafana dashboard for experiment {experiment.Id}: {url}")
            return url
        else:
            Log.E(f"Could not generate Grafana dashboard for experiment {experiment.Id}: "
                  f"{response.status} - {response.reason}")
            try: Log.E(f"Response data: {response.data}")
            except: pass
            return None

    @staticmethod
    def generateData(experiment: ExperimentRun) -> Dict:
        return {
            "dashboard": {
                "id": None,
                "uid": f"Run{experiment.Id}",
                "title": f"Experiment run {experiment.Id}",
                "tags": [],
                "style": "dark",
                "timezone": "browser",
                "editable": False,
                "hideControls": True,
                "graphTooltip": 1,
                "timepicker": {"time_options": [], "refresh_intervals": []},
                "templating": {"list": []},
                "annotations": {"list": []},
                "refresh": "5s",
                "schemaVersion": 17,
                "version": 1,
                "links": [],
                "panels": DashboardGenerator.generatePanels(experiment),
                "time": DashboardGenerator.generateTime(experiment)
            }
        }

    @staticmethod
    def generateTime(experiment: ExperimentRun):
        timeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"
        runner = experiment.Executor
        return {
            "from": str(runner.Started.strftime(timeFormat)),
            "to": str(runner.Finished.strftime(timeFormat)),
        }

    @staticmethod
    def generatePanels(experiment: ExperimentRun):
        name = "collectd_enb_cpu_vcpu"
        enbCpu = DashboardGenerator.panelBase(0, name, (9, 12, 0, 0), lines=True, percentage=False)
        enbCpu["targets"] = [
            DashboardGenerator.getTarget(
                "collectd_enb_cpu_vcpu",
                f'SELECT mean("{name}") FROM "{name}" WHERE (\"ExperimentId\" = "{str(experiment.Id)}")'
                f' AND $timeFilter GROUP BY time($__interval) fill(null)', "ASC", experiment.Id)
        ]

        return [enbCpu]

    @staticmethod
    def getTarget(name: str, query: str, order: str, expId: int) -> Dict:
        return {
            "hide": False,
            "measurement": name,
            "orderByTime": order,
            "policy": "default",
            "query": query,
            "rawQuery": False,
            "refId": "A",
            "resultFormat": "time_series",
            "groupBy": [
                {"params": ["$__interval"], "type": "time"},
                {"params": ["null"], "type": "fill"}
            ],
            "select": [
                [
                    {"params": [name], "type": "field"},
                    {"params": [], "type": "mean"}
                ]
            ],
            "tags": [{"key": "ExperimentId", "operator": "=", "value": str(expId)}]
        }

    @staticmethod
    def panelBase(id: int, name: str, pos: Tuple[int, int, int, int],
                  lines: bool = False, percentage: bool = False) -> Dict:
        return {
            "id": id,
            "title": name,
            "aliasColors": {},
            "bars": not lines,
            "dashLength": 10,
            "dashes": False,
            "fill": 1,
            "gridPos": {
                "h": pos[0], "w": pos[1],
                "x": pos[2], "y": pos[3]
            },
            "legend": {
                "avg": False, "current": False, "max": False, "min": False,
                "show": True, "total": False, "values": False
            },
            "lines": lines,
            "linewidth": 1,
            "nullPointMode": "null",
            "percentage": percentage,
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
                "buckets": None, "mode": "time","name": None,
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
