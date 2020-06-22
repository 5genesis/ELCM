from influxdb import InfluxDBClient
from .config import Config
from typing import Dict, List, Union
from datetime import datetime, timezone
from csv import DictWriter, DictReader, Sniffer
from os.path import abspath
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
        return f"InfluxPayload['{self.Measurement}' - Tags: {self.Tags} - " + \
            f"Points: [{', '.join(str(p) for p in self.Points)}]]"


class InfluxDb:
    client = None
    baseTags = {}

    @classmethod
    def initialize(cls):
        config = Config()

        influx = config.InfluxDb
        try:
            cls.client = InfluxDBClient(influx.Host, influx.Port,
                                        influx.User, influx.Password, influx.Database)
        except Exception as e:
            raise Exception(f"Exception while creating Influx client, please review configuration: {e}") from e

        metadata = config.Metadata
        cls.baseTags = {
            "appname": "ELCM",
            "facility": metadata.Facility,
            "host": metadata.HostIp,
            "hostname": metadata.HostName
        }

    @classmethod
    def BaseTags(cls) -> Dict[str, object]:
        if cls.client is None:
            cls.initialize()
        return cls.baseTags

    @classmethod
    def Send(cls, payload: InfluxPayload):
        if cls.client is None:
            cls.initialize()

        payload.Tags.update(cls.baseTags)
        cls.client.write_points(payload.Serialized)

    @classmethod
    def PayloadToCsv(cls, payload: InfluxPayload, outputFile: str):
        allKeys = {'Datetime', 'Timestamp'}
        for point in payload.Points:
            allKeys.update(point.Fields.keys())
        allKeys = sorted(list(allKeys))
        allKeys.extend(sorted(payload.Tags.keys()))

        # https://stackoverflow.com/a/3348664 (newline)
        with open(abspath(outputFile), 'w', encoding='utf-8', newline='') as output:
            csv = DictWriter(output, fieldnames=allKeys, restval='')
            csv.writeheader()
            for point in payload.Points:
                data = {'Datetime': point.Time, 'Timestamp': point.Time.timestamp()}
                data.update(point.Fields)
                data.update(payload.Tags)
                csv.writerow(data)

    @classmethod
    def CsvToPayload(cls, measurement: str, csvFile: str, delimiter: str, timestampKey: str,
                     tryConvert: bool = True, keysToRemove: List[str] = None) -> InfluxPayload:
        def _convert(value: str) -> Union[int, float, bool, str]:
            try: return int(value)
            except ValueError: pass

            try: return float(value)
            except ValueError: pass

            return {'true': True, 'false': False}.get(value.lower(), value)

        keysToRemove = [] if keysToRemove is None else keysToRemove

        if cls.client is None:
            cls.initialize()

        with open(csvFile, 'r', encoding='utf-8', newline='') as file:
            sniffer = Sniffer()
            if not sniffer.has_header(file.read(1024)):
                raise RuntimeError("CSV file does not seem to contain a header")
            file.seek(0)
            dialect = sniffer.sniff(file.read(1024), delimiters=delimiter)
            file.seek(0)

            header = file.readline()
            keys = [k.strip() for k in header.split(delimiter)]

            if timestampKey not in keys:
                raise RuntimeError(f"CSV file does not seem to contain timestamp ('{timestampKey}') values. "
                                   f"Keys in file: {keys}")

            csv = DictReader(file, fieldnames=keys, restval=None, dialect=dialect)
            payload = InfluxPayload(measurement)

            for row in csv:
                timestamp = datetime.fromtimestamp(float(row.pop(timestampKey)), tz=timezone.utc)
                point = InfluxPoint(timestamp)
                for key, value in row.items():
                    if key in keysToRemove:
                        continue
                    if tryConvert:
                        value = _convert(value)
                    point.Fields[key] = value
                payload.Points.append(point)

            return payload
