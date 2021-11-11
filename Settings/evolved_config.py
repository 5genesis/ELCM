from typing import Dict, List, Tuple, Optional
from Helper.log_level import Level
from .config_base import validable, enabledLoginRestApi, ConfigBase


class JenkinsApi(enabledLoginRestApi):
    def __init__(self, data: Dict):
        super().__init__(data, 'JenkinsApi', {})


class NefEmulator(enabledLoginRestApi):
    def __init__(self, data: Dict):
        super().__init__(data, 'NefEmulator', {})


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

    @property
    def NefEmulator(self):
        return NefEmulator(EvolvedConfig.data.get('NefEmulator', {}))

    def Validate(self):
        EvolvedConfig.Validation = []

        for entry in [self.JenkinsApi, self.NefEmulator]:
            EvolvedConfig.Validation.extend(entry.Validation)
