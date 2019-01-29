from Executor import Executor
from threading import Lock
import yaml
from typing import Dict


def synchronized(lock):
    def wrap(f):
        def new_funct(*args, **kwargs):
            lock.acquire()
            try:
                return f(*args, **kwargs)
            finally:
                lock.release()
        return new_funct
    return wrap


class Status:
    FILENAME = 'persistence.yml'

    lock = Lock()
    nextId = 0
    activeExecutors: Dict[int, Executor] = {}

    @classmethod
    @synchronized(lock)
    def Initialize(cls):
        with open(cls.FILENAME, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            cls.nextId = data['NextId']

    @classmethod
    @synchronized(lock)
    def Save(cls):
        data = {
            'NextId': cls.nextId
        }
        with open(cls.FILENAME, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False)

    @classmethod
    def GetNextId(cls):
        res = cls.nextId
        cls.nextId += 1
        cls.Save()
        return res

    @classmethod
    def CreateExecutor(cls) -> (int, Executor):
        executorId = cls.GetNextId()
        executor = Executor(params={'Id': executorId})
        cls.activeExecutors[executorId] = executor
        return executorId, executor

    @classmethod
    def DeleteExecutor(cls, executorId: int):
        cls.activeExecutors.pop(executorId)
