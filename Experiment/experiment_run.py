from Executor import PreRunner, Executor, PostRunner, ExecutorBase
from Data import ExperimentDescriptor
from typing import Dict, Optional
from enum import Enum, unique
from datetime import datetime
from tempfile import TemporaryDirectory
from Helper import Config, Serialize, Log
from Interfaces import DispatcherApi
from Composer import Composer, PlatformConfiguration


@unique
class CoarseStatus(Enum):
    Init, PreRun, Run, PostRun, Finished, Cancelled, Errored = range(7)


class ExperimentRun:
    dispatcher: DispatcherApi = None
    grafana = None

    def __init__(self, id: int, params: Dict):
        self.Id = id
        self.Params = params
        self.Params['Id'] = self.Id
        self.Params['Configuration'] = Composer.Compose(self.Descriptor)
        self.TempFolder = TemporaryDirectory(dir=Config().TempFolder)
        self.PreRunner = PreRunner(self.Params, tempFolder=self.TempFolder)
        self.Executor = Executor(self.Params, tempFolder=self.TempFolder)
        self.PostRunner = PostRunner(self.Params, tempFolder=self.TempFolder)
        self._coarseStatus = CoarseStatus.Init
        self._dashboardUrl = None
        self.Cancelled = False
        self.Created = datetime.utcnow()

        if self.dispatcher is None or self.grafana is None:
            from Helper import DashboardGenerator  # Delayed to avoid cyclic imports
            config = Config()
            self.dispatcher = DispatcherApi(config.Dispatcher.Host, config.Dispatcher.Port)
            self.grafana = DashboardGenerator(config.Grafana.Enabled, config.Grafana.Host,
                                              config.Grafana.Port, config.Grafana.Bearer,
                                              config.Grafana.ReportGenerator)

    @property
    def CoarseStatus(self):
        return self._coarseStatus

    @CoarseStatus.setter
    def CoarseStatus(self, value: CoarseStatus):
        if value != self._coarseStatus:
            self._coarseStatus = value
            self.dispatcher.UpdateExecutionData(self.Id, status=value.name)

    @property
    def DashboardUrl(self):
        return self._dashboardUrl

    @DashboardUrl.setter
    def DashboardUrl(self, value: str):
        if value != self._dashboardUrl:
            self._dashboardUrl = value
            self.dispatcher.UpdateExecutionData(self.Id, dashboardUrl=value)

    @property
    def Status(self) -> str:
        if self.CoarseStatus == CoarseStatus.PreRun:
            return f'PreRun: {self.PreRunner.Status.name}'
        elif self.CoarseStatus == CoarseStatus.Run:
            return f'Run: {self.Executor.Status.name}'
        elif self.CoarseStatus == CoarseStatus.PostRun:
            return f'PostRun: {self.PostRunner.Status.name}'
        else:
            return self.CoarseStatus.name

    @property
    def PerCent(self) -> int:
        current = self.CurrentChild
        return current.PerCent if current is not None else 0

    @property
    def LastMessage(self) -> str:
        current = self.CurrentChild
        return current.LastMessage if current is not None else 'Not active child'

    @property
    def Messages(self) -> [str]:
        current = self.CurrentChild
        return current.Messages if current is not None else []

    @property
    def Active(self) -> bool:
        return self.CoarseStatus.value < CoarseStatus.Finished.value

    @property
    def Descriptor(self) -> Optional[ExperimentDescriptor]:
        return self.Params.get('Descriptor', None)

    @property
    def Configuration(self) -> Optional[PlatformConfiguration]:
        return self.Params.get('Configuration', None)

    @property
    def CurrentChild(self) -> Optional[ExecutorBase]:
        if self.CoarseStatus == CoarseStatus.PreRun: return self.PreRunner
        if self.CoarseStatus == CoarseStatus.Run: return self.Executor
        if self.CoarseStatus == CoarseStatus.PostRun: return self.PostRunner
        return None

    def Cancel(self):
        current = self.CurrentChild
        if current is not None:
            current.RequestStop()
        self.CoarseStatus = CoarseStatus.Cancelled

    def PreRun(self):
        self.CoarseStatus = CoarseStatus.PreRun
        self.PreRunner.Start()

    def Run(self):
        self.CoarseStatus = CoarseStatus.Run
        self.Executor.Start()

    def PostRun(self):
        self.CoarseStatus = CoarseStatus.PostRun
        self.PostRunner.Start()

    def Advance(self):
        if not self.Active:
            return
        elif self.CoarseStatus == CoarseStatus.Init:
            self.PreRun()
        elif self.CoarseStatus == CoarseStatus.PreRun:
            if self.PreRunner.HasFailed:
                self.CoarseStatus = CoarseStatus.Errored
                Log.I(f'Experiment {self.Id} has failed on PreRun')
                self.handleExperimentEnd()
                return
            if self.PreRunner.Finished:
                self.Run()
        elif self.CoarseStatus == CoarseStatus.Run:
            if self.Executor.HasFailed:
                self.CoarseStatus = CoarseStatus.Errored
                Log.I(f'Experiment {self.Id} has failed on Run')
                self.handleExperimentEnd()
                return
            if self.Executor.Finished:
                self.PostRun()
        elif self.CoarseStatus == CoarseStatus.PostRun:
            if self.PostRunner.HasFailed:
                Log.I(f'Experiment {self.Id} has failed on Run')
                self.CoarseStatus = CoarseStatus.Errored
            elif self.PostRunner.Finished:
                self.CoarseStatus = CoarseStatus.Finished
            self.handleExperimentEnd()

    def handleExperimentEnd(self):
        # Try to create the dashboard even in case of error, there might be results to display
        try:
            Log.D(f"Trying to generate dashboard for experiment {self.Id}")
            self.Configuration.ExpandDashboardPanels(self)
            url = self.grafana.Create(self)
            self.DashboardUrl = url
        except Exception as e:
            Log.E(f"Exception while handling experiment end ({self.Id}): {e}")
        finally:
            Log.D(f"Clearing temp folder for experiment {self.Id}")
            self.TempFolder.cleanup()

    def Serialize(self) -> Dict:
        data = {
            'Id': self.Id,
            'Created': Serialize.DateToString(self.Created),
            'CoarseStatus': self.CoarseStatus.name,
            'Cancelled': self.Cancelled
        }
        return data

    def Save(self):
        self.PreRunner.Save()
        self.Executor.Save()
        self.PostRunner.Save()
        data = self.Serialize()
        path = Serialize.Path('Experiment', str(self.Id))
        Serialize.Save(data, path)

    @classmethod
    def Digest(cls, id: str) -> Dict:
        return Serialize.Load(Serialize.Path('Experiment', id))
