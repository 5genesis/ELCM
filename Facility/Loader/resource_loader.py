from Helper import Level
from .loader_base import Loader
from ..resource import Resource
from typing import Dict


class ResourceLoader(Loader):
    resources: Dict[str, Resource] = {}

    @classmethod
    def ProcessFile(cls, path: str) -> [(Level, str)]:
        validation = []
        try:
            data, v = cls.LoadFile(path)
            validation.extend(v)
            resource = Resource(data)
            if resource.Id in cls.resources.keys():
                validation.append((Level.WARNING, f'Redefining Resource {resource.Id}'))
            cls.resources[resource.Id] = resource
        except Exception as e:
            validation.append((Level.ERROR, f'Exception loading Resource file {path}: {e}'))
        return validation

    @classmethod
    def Clear(cls):
        cls.resources = {}
