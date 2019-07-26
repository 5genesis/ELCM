from influxdb import InfluxDBClient
from .config import Config
from typing import Dict, List
from datetime import datetime
import re


class InfluxPoint:
    def __init__(self, time: datetime):
        self.Time = time
        self.Fields: Dict[str, object] = {}

    def __str__(self):
        return f"<{self.Time} {self.Fields}>"


class InfluxPayload:
    def __init__(self, measurement: str):
        self.Measurement = re.sub(r'\W+', '_', measurement)  # Replace spaces and non-alphanumeric characters with _
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

    def __str__(self):
        return f"InfluxPayload['{self.Measurement}' - Tags: {self.Tags} - Points: {self.Points}]"


class InfluxDb:
    client = None
    baseTags = {}

    @classmethod
    def initialize(cls):
        # cls.client = InfluxDBClient("triangle.uma.es", "15003", "admin", "admin", "mydb")
        # return
        config = Config()
        influx = config.InfluxDb
        cls.client = InfluxDBClient(influx.Host, influx.Port,
                                    influx.User, influx.Password, influx.Database)

        metadata = config.Metadata
        cls.baseTags = {
            "appname": "ELCM",
            "facility": metadata.Facility,
            "host": metadata.HostIp,
            "hostname": metadata.HostName
        }

    @classmethod
    def Send(cls, payload: InfluxPayload):
        if cls.client is None:
            cls.initialize()

        payload.Tags.update(cls.baseTags)
        cls.client.write_points(payload.Serialized)

