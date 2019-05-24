from Helper import Log
from REST import RestClient
from Experiment import ExperimentRun
import json
from typing import Dict, Tuple, Optional


class DashboardGenerator(RestClient):
    def __init__(self, enabled: bool, host: str, port: int, bearer: str):
        if enabled: super().__init__(host, port, "/api")
        self.enabled = enabled
        self.bearer = bearer
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f"Bearer {self.bearer}"
        }

    def Create(self, experiment: ExperimentRun) -> Optional[str]:
        if not self.enabled: return None

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
        res = []
        panels = experiment.Configuration.DashboardPanels
        for index, panel in zip(range(len(panels)), panels):
            res.append(panel.Generate(index, experiment.Id))
        return res
