from threading import Lock
from Helper import Serialize, IO
from Utils import synchronized
from os.path import dirname


class Status:
    FILENAME = 'persistence.yml'

    lock = Lock()
    nextId = 0

    _persistence_yml = {'NextId': 0}

    @classmethod
    @synchronized(lock)
    def Initialize(cls):
        path = Serialize.Path('persistence')

        if not IO.EnsureFolder(dirname(path)):
            Serialize.Save(cls._persistence_yml, path)

        data = Serialize.Load(path)
        cls.nextId = data['NextId']

    @classmethod
    @synchronized(lock)
    def Save(cls):
        data = {'NextId': cls.nextId}
        Serialize.Save(data, Serialize.Path('persistence'))

    @classmethod
    def NextId(cls):
        res = cls.nextId
        cls.nextId += 1
        cls.Save()
        return res

    @classmethod
    def PeekNextId(cls):
        return cls.nextId
