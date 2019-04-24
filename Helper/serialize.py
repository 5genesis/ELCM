from os.path import join, abspath, exists, dirname, isdir, isfile
from os import makedirs, listdir
import yaml
from typing import Dict, Optional, List as _List, Tuple
from datetime import datetime


class Serialize:
    BASE = 'Persistence'
    FORMAT = '%a %b %d %H:%M:%S %Y'

    @classmethod
    def Path(cls, *args: str):
        tokens = list(args)
        tokens[-1] = f'{tokens[-1]}.yml'
        return abspath(join(cls.BASE, *tokens))

    @classmethod
    def List(cls, folders: bool = False, fullPath: bool = False, *args: str) -> _List[str]:
        path = abspath(join(cls.BASE, *args))
        if not exists(dirname(path)): return []
        items = [i for i in listdir(path)]
        filter = isdir if folders else isfile
        filtered = [i for i in items if filter(join(path, i))]
        if fullPath:
            return [abspath(join(path, i)) for i in filtered]
        else:
            return [i.replace('.yml', '') for i in filtered]

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
    def Unroll(data: Dict, *args: str) -> _List[object]:
        res = []
        for arg in args:
            res.append(data.get(arg, None))
        return res

    @staticmethod
    def CheckKeys(data: Dict, *args: str) -> Tuple[bool, _List[str]]:
        missing = []
        for key in args:
            if key not in data.keys(): missing.append(key)
        return len(missing) == 0, missing
