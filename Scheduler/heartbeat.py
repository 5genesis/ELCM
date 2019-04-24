from Helper import Child
from typing import Dict
from Helper import Level
from time import sleep
from Status import ExperimentQueue


class Beat(Child):
    def __init__(self, params: Dict):
        super().__init__(f"HeartBeat")
        self.params = params

    def Run(self):
        while not self.stopRequested:
            self.Broadcast(Level.DEBUG, 'Alive')
            ExperimentQueue.UpdateAll()
            Beat.wait()

    @staticmethod
    def wait():
        sleep(10)


class HeartBeat:
    beat = None

    @classmethod
    def Initialize(cls):
        if cls.beat is None:
            cls.beat = Beat(params={})
            cls.beat.Start()

