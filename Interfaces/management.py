from Executor import Executor
from random import randrange


class Management:
    registry = {}

    @classmethod
    def HasResources(cls, executor: Executor):
        id = executor.Id
        if id not in cls.registry.keys():
            cls.registry[id] = randrange(0, 3)
        if cls.registry[id] == 0:
            cls.registry.pop(id)
            return True
        else:
            cls.registry[id] -= 1
            return False
