from REST import RestClient
from Experiment import ExperimentRun
import json
from typing import Dict


class DashboardGenerator(RestClient):
    timeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, host: str, port: int, bearer: str):
        super().__init__(host, port, "/api")
        self.bearer = bearer
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f"Bearer {self.bearer}"
        }

    def Create(self, experiment: ExperimentRun) -> str:
        body = self.generateData(experiment)
        response = self.httpPost(f"{self.api_url}/dashboards/db", self.headers, json.dumps(body))
        return "" #TODO: Return the dashboard URL

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
    def generatePanels(experiment: ExperimentRun):
        return []

    @staticmethod
    def generateTime(experiment: ExperimentRun):
        return {
            "from": str(experiment.PreRunner.Started.strftime(DashboardGenerator.timeFormat)),
            "to": str(experiment.PostRunner.Finished.strftime(DashboardGenerator.timeFormat)),
        }
