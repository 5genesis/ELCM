from Task import Task
from Helper import Level
from time import sleep


class CsvToInflux(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Csv To Influx", parent, params, logMethod, None)

    def Run(self):
        try: executionId = self.params['ExecutionId']
        except KeyError:
            self.Log(Level.ERROR, "ExecutionId value not defined, please review the Task configuration.")
            return

        try: csvFile = self.params["CSV"]
        except KeyError:
            self.Log(Level.ERROR, "CSV file not defined, please review the Task configuration.")
            return

        try: measurement = self.params["Measurement"]
        except KeyError:
            self.Log(Level.ERROR, "Measurement not defined, please review the Task configuration.")
            return

        delimiter = self.params.get("Delimiter", ',')
        timestamp = self.params.get("Timestamp", "Timestamp")
        tryConvert = self.params.get("Convert", True)

        try:
            from Helper import InfluxDb, InfluxPayload  # Delayed to avoid cyclic imports
            self.Log(Level.INFO, "Converting csv file to payload")
            keysToRemove = ['ExecutionId', *InfluxDb.BaseTags()]
            self.Log(Level.DEBUG, f"The following columns will be replaced (as tags): {keysToRemove}")
            payload = InfluxDb.CsvToPayload(measurement, csvFile, delimiter, timestamp,
                                            tryConvert=tryConvert, keysToRemove=keysToRemove)
            payload.Tags = {'ExecutionId': str(executionId)}
            self.Log(Level.DEBUG, f"Payload: {payload}")
        except Exception as e:
            self.Log(Level.ERROR, f"Exception while converting CSV: {e}")
            return

        try:
            self.Log(Level.INFO, "Sending payload to InfluxDb")
            InfluxDb.Send(payload)
        except Exception as e:
            self.Log(Level.ERROR, f"Exception while sending CSV values to Influx: {e}")
