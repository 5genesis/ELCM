from random import randrange


class Management:
    registry = {}

    @classmethod
    def HasResources(cls, executorId):
        if executorId not in cls.registry.keys():
            cls.registry[executorId] = randrange(0, 3)
        if cls.registry[executorId] == 0:
            cls.registry.pop(executorId)
            return True
        else:
            cls.registry[executorId] -= 1
            return False
