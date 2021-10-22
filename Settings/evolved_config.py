from typing import Dict, List, Tuple, Optional
from Helper.log_level import Level
from .config_base import validable, restApi, ConfigBase


class JenkinsApi(restApi):
    def __init__(self, data: Dict):
        defaults = {
            'Enabled': (False, Level.WARNING)
        }
        super().__init__(data, 'JenkinsApi', defaults)

    @property
    def Enabled(self):
        return self._keyOrDefault('Enabled')

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        if self.Enabled:
            return super().Validation
        else:
            return [(Level.INFO, "Jenkins API is disabled")]


class EvolvedConfig(ConfigBase):
    data = None
    Validation: List[Tuple['Level', str]] = []

    def __init__(self, forceReload=False):
        super().__init__('evolved5g.yml', 'Settings/default_evolved_config')
        if self.data is None or forceReload:
            EvolvedConfig.data = self.Reload()
            self.Validate()

    @property
    def JenkinsApi(self):
        return JenkinsApi(EvolvedConfig.data.get('JenkinsApi', {}))

    def Validate(self):
        for entry in [self.JenkinsApi, ]:
            EvolvedConfig.Validation.extend(entry.Validation)
