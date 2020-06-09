from typing import Dict, Union
from .experiment_run import ExperimentRun
from Executor import ExecutorBase
from re import finditer
from Helper import Config
from json import dumps


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
            "@{ExecutionId}": context.ExecutionId,
            "@{SliceId}": context.Params.get("SliceId", "None"),
            "@{Application}": context.Descriptor.Application,
            "@{JSONParameters}": dumps(context.Descriptor.Parameters, indent=None),
            # Configuration values
            "@{TapFolder}": config.Tap.Folder,
            "@{TapResults}": config.Tap.Results,
        }

        expanded = item
        for key, value in replacements.items():
            expanded = expanded.replace(key, str(value))

        # Expand custom values published by Run.Publish and parameters
        for match in [m for m in finditer(r'@\[(.*?)]', item)]:
            all = match.group()
            capture = match.groups()[0]
            if ':' in capture:
                key, default = capture.split(':')
            else:
                key = capture
                default = '<<UNDEFINED>>'

            collection = None
            group = None
            if '.' in key:
                group, key = key.split('.')
                if group == "Params":
                    collection = context.Descriptor.Parameters
                elif group == "Publish":
                    collection = context.params
            else:
                collection = context.params

            value = collection.get(key, default) if collection is not None else f'<<UNKNOWN GROUP {group}>>'
            expanded = expanded.replace(all, str(value))

        return expanded
