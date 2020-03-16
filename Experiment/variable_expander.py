from typing import Dict, Union
from .experiment_run import ExperimentRun
from Executor import ExecutorBase
from re import finditer
from Helper import Config


class Expander:
    @classmethod
    def ExpandDict(cls, dict: Dict, context: Union[ExecutorBase, ExperimentRun]):
        config = Config()
        return cls.expandParams(dict, context, config)

    @classmethod
    def expandParams(cls, item: object, context: Union[ExecutorBase, ExperimentRun], config: Config) -> object:
        if isinstance(item, dict):
            res = {}
            for key, value in item.items():
                res[key] = cls.expandParams(value, context, config)
        elif isinstance(item, list) or isinstance(item, tuple):
            res = []
            for value in item:
                res.append(cls.expandParams(value, context, config))
        elif isinstance(item, str):
            res = cls.expand(item, context, config)
        else:
            res = item
        return res

    @classmethod
    def expand(cls, item: str, context: Union[ExecutorBase, ExperimentRun], config: Config) -> str:
        replacements = {
            # Dynamic values
            "@{TempFolder}": context.TempFolder,
            "@{ExecutionId}": context.Id,
            "@{SliceId}": context.Params.get("SliceId", "None"),
            # Configuration values
            "@{TapFolder}": config.Tap.Folder,
            "@{TapResults}": config.Tap.Results
        }

        expanded = item
        for key, value in replacements.items():
            expanded = expanded.replace(key, str(value))

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
