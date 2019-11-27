from typing import Dict, Union
from .experiment_run import ExperimentRun
from Executor import ExecutorBase
from re import finditer


class Expander:
    @classmethod
    def ExpandDict(cls, dict: Dict, context: Union[ExecutorBase, ExperimentRun]):
        return cls.expandParams(dict, context)

    @classmethod
    def expandParams(cls, item: object, context: Union[ExecutorBase, ExperimentRun]) -> object:
        if isinstance(item, dict):
            res = {}
            for key, value in item.items():
                res[key] = cls.expandParams(value, context)
        elif isinstance(item, list) or isinstance(item, tuple):
            res = []
            for value in item:
                res.append(cls.expandParams(value, context))
        elif isinstance(item, str):
            res = cls.expand(item, context)
        else:
            res = item
        return res

    @classmethod
    def expand(cls, item: str, context: Union[ExecutorBase, ExperimentRun]) -> str:
        expanded = item
        expanded = expanded.replace("@{ExecutionId}", str(context.Id))
        expanded = expanded.replace("@{SliceId}", str(context.Params.get("SliceId", "None")))

        # Expand custom values published by Run.Publish
        for match in [m for m in finditer(r'@\[(.*?)]', item)]:
            all = match.group()
            capture = match.groups()[0]
            if ':' in capture:
                key, default = capture.split(':')
            else:
                key = capture
                default = '<<UNDEFINED>>'
            value = context.params.get(key, default)
            expanded = expanded.replace(all, str(value))

        return expanded
