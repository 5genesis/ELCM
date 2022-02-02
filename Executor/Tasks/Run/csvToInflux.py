from Task import Task
from Helper import Level
from time import sleep


class CsvToInflux(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Csv To Influx", parent, params, logMethod, None)
        self.paramRules = {
            'ExecutionId': (None, True),
            'CSV': (None, True),
            'Measurement': (None, True),
            'Delimiter': (',', False),
            'Timestamp': ('Timestamp', False),
            'Convert': (True, False)
        }

    def Run(self):
        executionId = self.params['ExecutionId']
        csvFile = self.params["CSV"]
        measurement = self.params["Measurement"]
        delimiter = self.params["Delimiter"]
        timestamp = self.params["Timestamp"]
        tryConvert = self.params["Convert"]

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
            self.SetVerdictOnError()
            return

        try:
            self.Log(Level.INFO, "Sending payload to InfluxDb")
            InfluxDb.Send(payload)
        except Exception as e:
            self.Log(Level.ERROR, f"Exception while sending CSV values to Influx: {e}")
            self.SetVerdictOnError()
