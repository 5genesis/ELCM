from influxdb import InfluxDBClient
from .config import Config
from typing import Dict, List, Union
from datetime import datetime, timezone
from csv import DictWriter, DictReader, Dialect, QUOTE_NONE
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

    @classmethod
    def FromEastWestData(cls, measurement: str, tags: Dict[str, str], header: List[str], points: List):
        res = InfluxPayload(measurement)
        res.Tags = tags
        for point in points:
            timestamp, values = point
            influxPoint = InfluxPoint(datetime.fromtimestamp(timestamp))
            for key, value in zip(header, values):
                influxPoint.Fields[key] = value
            res.Points.append(influxPoint)
        return res


class baseDialect(Dialect):
    delimiter = ','
    escapechar = None
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quotechar = ''
    quoting = QUOTE_NONE


class InfluxDb:
    client = None
    database = None
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
        cls.database = influx.Database

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
            header = file.readline()
            keys = [k.strip() for k in header.split(delimiter)]

            if timestampKey not in keys:
                raise RuntimeError(f"CSV file does not seem to contain timestamp ('{timestampKey}') values. "
                                   f"Keys in file: {keys}")

            dialect = baseDialect()
            dialect.delimiter = str(delimiter.strip())

            csv = DictReader(file, fieldnames=keys, restval=None, dialect=dialect)
            payload = InfluxPayload(measurement)

            for row in csv:
                timestampValue = float(row.pop(timestampKey))
                try:
                    timestamp = datetime.fromtimestamp(timestampValue, tz=timezone.utc)
                except OSError:
                    # value outside of bounds, maybe because it's specified in milliseconds instead of seconds
                    timestamp = datetime.fromtimestamp(timestampValue/1000.0, tz=timezone.utc)

                point = InfluxPoint(timestamp)
                for key, value in row.items():
                    if key in keysToRemove:
                        continue
                    if tryConvert:
                        value = _convert(value)
                    point.Fields[key] = value
                payload.Points.append(point)

            return payload

    @classmethod
    def GetExecutionMeasurements(cls, executionId: int) -> List[str]:
        if cls.client is None:
            cls.initialize()

        reply = cls.client.query(f'SHOW measurements WHERE ExecutionId =~ /^{executionId}$/')
        return [e['name'] for e in reply['measurements']]


    @classmethod
    def GetMeasurement(cls, executionId: int, measurement: str) -> List[InfluxPayload]:
        def _getTagSet(point, tags):
            values = [str(point[tag]) for tag in tags]
            return ','.join(values)

        def _getDateTime(value: str):
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")

        if cls.client is None:
            cls.initialize()

        # Retrieve the list of tags from the server, to separate from fields
        reply = cls.client.query(f"show tag keys on {cls.database} from {measurement}")
        tags = sorted([t['tagKey'] for t in reply.get_points()])

        pointsPerTagSet = {}

        # Retrieve all points, separated depending on the tags
        reply = cls.client.query(f'SELECT * FROM "{measurement}" WHERE ExecutionId =~ /^{executionId}$/')
        for point in reply.get_points():
            tagSet = _getTagSet(point, tags)
            if tagSet not in pointsPerTagSet.keys():
                pointsPerTagSet[tagSet] = []
            pointsPerTagSet[tagSet].append(point)

        res = []

        # Process each set of points as a separate InfluxPayload
        for points in pointsPerTagSet.values():
            payload = InfluxPayload(f'Remote_{measurement}')
            for tag in tags:
                payload.Tags[tag] = points[0][tag]

            for point in points:
                timestamp = point.pop('time')
                influxPoint = InfluxPoint(_getDateTime(timestamp))
                for key in [f for f in point.keys() if f not in tags]:
                    influxPoint.Fields[key] = point[key]
                payload.Points.append(influxPoint)

            res.append(payload)

        return res

