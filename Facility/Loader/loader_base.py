import yaml
from Helper import Level
from typing import Callable, List, Dict
from os.path import join


class Loader:
    @classmethod
    def EnsureFolder(cls, path: str) -> [(Level, str)]:
        from Helper import IO
        validation = []
        if not IO.EnsureFolder(path):
            validation.append((Level.INFO, f'Auto-generated folder: {path}'))
        return validation

    @classmethod
    def LoadFolder(cls, path: str, kind: str) -> [(Level, str)]:
        from Helper import IO
        ignored = []
        validation = []
        for file in IO.ListFiles(path):
            if file.endswith('.yml'):
                validation.append((Level.INFO, f'Loading {kind}: {file}'))
                v = cls.ProcessFile(join(path, file))
                validation.extend(v)
            else:
                ignored.append(file)
        if len(ignored) != 0:
            validation.append((Level.WARNING,
                               f'Ignored the following files on the {kind}s folder: {(", ".join(ignored))}'))
        return validation

    @classmethod
    def LoadFile(cls, path: str) -> ((Dict | None), [(Level, str)]):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                raw = yaml.safe_load(file)
                return raw, []
        except Exception as e:
            return None, [(Level.ERROR, f"Unable to load file '{path}': {e}")]


    @classmethod
    def ProcessFile(cls, path: str):
        raise NotImplementedError
