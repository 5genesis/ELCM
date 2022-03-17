from Helper import Level
from .loader_base import Loader
from ..resource import Resource
from typing import Dict


class ResourceLoader(Loader):
    resources: Dict[str, Resource] = {}

    @classmethod
    def ProcessData(cls, data: Dict) -> [(Level, str)]:
        validation = []

        resource = Resource(data)
        if resource.Id in cls.resources.keys():
            validation.append((Level.WARNING, f'Redefining Resource {resource.Id}'))
        cls.resources[resource.Id] = resource

        return validation

    @classmethod
    def Clear(cls):
        cls.resources = {}

    @classmethod
    def GetCurrentResources(cls):
        return cls.resources
