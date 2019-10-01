from typing import Dict, Union
from .experiment_run import ExperimentRun
from Executor import ExecutorBase


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
        return expanded
