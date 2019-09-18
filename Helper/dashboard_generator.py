from Helper import Log
from REST import RestClient
from Experiment import ExperimentRun
import json
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta


class DashboardGenerator(RestClient):
    def __init__(self, enabled: bool, host: str, port: int, bearer: str, generatorUrl: str):
        if enabled: super().__init__(host, port, "/api")
        self.enabled = enabled
        self.bearer = bearer
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f"Bearer {self.bearer}"
        }
        self.reportGeneratorUrl = generatorUrl

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

    def generateData(self, experiment: ExperimentRun) -> Dict:
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
                "panels": self.generatePanels(experiment),
                "time": self.generateTime(experiment),
                "links": self.generateLinks(experiment)
            }
        }

    def generateTime(self, experiment: ExperimentRun) -> Dict:
        timeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"
        runner = experiment.Executor
        return {
            # Grafana expects to find this values in it's own timezone (currently GMT+2)
            "from": str((runner.Started - timedelta(hours=0)).strftime(timeFormat)),
            "to": str((runner.Finished - timedelta(hours=0)).strftime(timeFormat) if not runner.HasFailed
                      else (datetime.utcnow() - timedelta(hours=2)).strftime(timeFormat)),
        }
        return {
            "from": "2019-08-29T10:53:00.000Z", #str(runner.Started.strftime(timeFormat)),
            "to": "2019-08-29T10:56:00.000Z" #str(runner.Finished.strftime(timeFormat) if not runner.HasFailed
                      #else datetime.utcnow().strftime(timeFormat)),
        }

    def generatePanels(self, experiment: ExperimentRun) -> List[Dict]:
        res = []
        panels = experiment.Configuration.DashboardPanels
        for index, panel in zip(range(len(panels)), panels):
            res.append(panel.Generate(index, experiment.Id))
        return res

    def generateLinks(self, experiment: ExperimentRun) -> List[Dict]:
        if self.reportGeneratorUrl is not None and len(self.reportGeneratorUrl) > 0:
            report = {
                "icon": "doc",
                "includeVars": True,
                "keepTime": True,
                "tags": [],
                "targetBlank": True,
                "title": "PDF Report",
                "tooltip": "Retrieve a PDF report generated from this dashboard.",
                "type": "link",
                "url": f"{self.reportGeneratorUrl}/api/v5/report/Run{experiment.Id}?"
                       f"apitoken={self.bearer}&template=5genesis"
            }
            return [report]
        else:
            return []
