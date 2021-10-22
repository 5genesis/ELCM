from typing import Dict, List, Tuple, Optional
from Helper.log_level import Level
from REST import RestClient


class validable:
    def __init__(self, data: Dict, section: str,
                 defaults: Dict[str, Tuple[Optional[object], "Level"]]):
        self.data = data
        self.section = section
        self.defaults = defaults

    def _keyOrDefault(self, key: str):
        if key in self.data.keys():
            return self.data[key]
        else:
            default = self.defaults.get(key, None)
            return default[0] if default is not None else None

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        res = []
        for key in self.defaults.keys():
            if key not in self.data:
                default, level = self.defaults[key]
                defaultText = f", using default '{default}'" if default is not None else ""
                res.append((level, f"'{key}' not defined under '{self.section}'{defaultText}"))
        if len(res) == 0:
            values = '; '.join([f'{key}: {self.data[key]}' for key in self.defaults.keys()])
            res.append((Level.INFO, f'{self.section} [{values}]'))
        return res


class restApi(validable):
    def __init__(self, data: Dict, section: str, defaults: Dict[str, Tuple[Optional[object], "Level"]]):
        if 'Host' not in defaults.keys(): defaults['Host'] = (None, Level.ERROR)
        if 'Port' not in defaults.keys(): defaults['Port'] = (None, Level.ERROR)
        super().__init__(data, section, defaults)

    @property
    def Host(self):
        return self._keyOrDefault('Host')

    @property
    def Port(self):
        return self._keyOrDefault('Port')

    @property
    def Validation(self) -> List[Tuple['Level', str]]:
        res = super().Validation
        if all([e[0] == Level.INFO for e in res]):
            # No errors, but check if a rest server can be created with the configuration
            try:
                _ = RestClient(self.Host, self.Port, "")
            except Exception as e:
                res.append((Level.ERROR, f'Exception creating {self.section} client: {e}'))
        return res