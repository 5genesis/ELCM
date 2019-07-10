from influxdb import InfluxDBClient
from .config import Config
from typing import Dict, List
from datetime import datetime


class InfluxPoint:
    def __init__(self, time: datetime):
        self.Time = time
        self.Fields: Dict[str, object] = {}


class InfluxPayload:
    def __init__(self, measurement: str):
        self.Measurement = measurement
        self.Tags: Dict[str, str] = {}
        self.Points: List[InfluxPoint] = []

    @property
    def Serialized(self):
        data = []
        for point in self.Points:
            data.append(
                {'measurement': self.Measurement,
                 'tags': self.Tags,
                 'time': point.Time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                 'fields': point.Fields}
            )
        return data


class InfluxDb:
    client = None

    @classmethod
    def initialize(cls):
        config = Config().InfluxDb
        cls.client = InfluxDBClient(config.Host, config.Port,
                                    config.User, config.Password, config.Database)

    @classmethod
    def Send(cls, payload: InfluxPayload):
        if cls.client is None:
            cls.initialize()

        cls.client.write_points(payload.Serialized)

