from threading import Lock
import yaml


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
