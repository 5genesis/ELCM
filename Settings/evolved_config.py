from typing import Dict, List, Tuple, Optional
from Helper.log_level import Level
from .config_base import validable, restApi, ConfigBase


class JenkisApi(restApi):
    def __init__(self, data: Dict):
        defaults = {
            'Enabled': (False, Level.WARNING)
        }
        super().__init__(data, 'Portal', defaults)

    @property
    def Enabled(self):
        return self._keyOrDefault('Enabled')


class EvolvedConfig(ConfigBase):
    data = None
    Validation: List[Tuple['Level', str]] = []

    def __init__(self):
        super().__init__('evolved5g.yml', 'Settings/default_evolved_config')
        if self.data is None:
            EvolvedConfig.data = self.Reload()
        self.Validate()

    @property
    def Portal(self):
        return JenkisApi(EvolvedConfig.data.get('Portal', {}))

    def Validate(self):
        pass
