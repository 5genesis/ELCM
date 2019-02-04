from os.path import join, abspath, exists, dirname
from os import makedirs
import yaml
from typing import Dict, Optional, List
from datetime import datetime


class Serialize:
    BASE = 'Persistence'
    FORMAT = '%a %b %d %H:%M:%S %Y'

    @classmethod
    def Path(cls, *args):
        return abspath(join(cls.BASE, *args))

    @classmethod
    def Save(cls, data, path):
        if not exists(dirname(path)): makedirs(dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as out:
            yaml.safe_dump(data, out, default_flow_style=False, allow_unicode=True)

    @classmethod
    def Load(cls, path) -> Dict:
        with open(path, 'r', encoding='utf-8') as input:
            return yaml.safe_load(input)

    @classmethod
    def DateToString(cls, date) -> Optional[str]:
        return date.strftime(cls.FORMAT) if date is not None else None

    @classmethod
    def StringToDate(cls, string: str) -> Optional[datetime]:
        return datetime.strptime(string, cls.FORMAT) if string is not None else None

    @staticmethod
    def Unroll(data: Dict, *args) -> List:
        res = []
        for arg in args:
            res.append(data.get(arg, None))
        return res
