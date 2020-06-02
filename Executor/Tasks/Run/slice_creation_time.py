from Task import Task
from Interfaces import Management
from Helper import Level
from time import sleep
from datetime import datetime, timezone


class SliceCreationTime(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Slice Creation Time Measurement", parent, params, logMethod, None)

    def Run(self):
        executionId = self.params['ExecutionId']
        waitForRunning = self.params['WaitForRunning']
        timeout = self.params.get('Timeout', None)
        sliceId = self.params['SliceId']
        count = 0

        if waitForRunning:
            self.Log(Level.INFO, f"Waiting for slice to be running. Timeout: {timeout}")
            while True:
                count += 1
                status = Management.SliceManager().CheckSlice(sliceId).get('status', '<SliceManager check error>')
                self.Log(Level.DEBUG, f'Slice {sliceId} status: {status} (retry {count})')
                if status == 'Running' or (timeout is not None and timeout >= count): break
                else: sleep(1)

        self.Log(Level.INFO, f"Reading deployment times for slice {sliceId}")
        times = Management.SliceManager().SliceCreationTime(sliceId)
        self.Log(Level.DEBUG, f"Received times: {times}")

        self.Log(Level.INFO, f"Generating results payload")
        from Helper import InfluxDb, InfluxPayload, InfluxPoint  # Delayed to avoid cyclic imports

        payload = InfluxPayload("Slice Creation Time")
        payload.Tags = {'ExecutionId': str(executionId)}
        point = InfluxPoint(datetime.now(timezone.utc))

        for key in ["Slice_Deployment_Time", "Placement_Time", "Provisioning_Time"]:
            value = times.get(key, "N/A")
            if value != "N/A":
                point.Fields[key] = float(value)

        payload.Points.append(point)
        self.Log(Level.DEBUG, f"Payload: {payload}")
        self.Log(Level.INFO, f"Sending results to InfluxDb")
        InfluxDb.Send(payload)

        # TODO: Artificial wait until the slice is 'configured'
        # TODO: In the future the slice manager should also report this status
        sleep(60)
