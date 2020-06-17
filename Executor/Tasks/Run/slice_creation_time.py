from Task import Task
from Interfaces import Management
from Helper import Level
from time import sleep
from datetime import datetime, timezone
from os.path import join
import json


class SliceCreationTime(Task):
    """Based on slice_creation_time: https://github.com/medianetlab/katana-slice_manager
    (https://github.com/medianetlab/katana-slice_manager/blob/master/slice_creation_time/sct/sct)"""

    def __init__(self, logMethod, parent, params):
        super().__init__("Slice Creation Time Measurement", parent, params, logMethod, None)

    def Run(self):
        executionId = self.params.get('ExecutionId', None)
        nestFile = self.params.get("NEST", None)
        iterations = self.params.get("Iterations", 25)
        csvFile = self.params.get("CSV", None)
        timeout = self.params.get("Timeout", None)
        pollTime = 5

        if executionId is None:
            self.Log(Level.ERROR, "ExecutionId value not defined, please review the Task configuration.")
            return

        if nestFile is None:
            self.Log(Level.ERROR, "NEST value not defined, please review the Task configuration.")
            return

        try:
            with open(nestFile, 'r', encoding='utf-8') as input:
                nestData = json.load(input)
        except Exception as e:
            self.Log(Level.ERROR, f"Exception while reading NEST file: {e}")
            return

        from Helper import InfluxDb, InfluxPayload, InfluxPoint  # Delayed to avoid cyclic imports
        payload = InfluxPayload("Slice Creation Time")
        payload.Tags = {'ExecutionId': str(executionId)}
        sliceManager = Management.SliceManager()
        nestData = json.dumps(nestData)

        for iteration in range(iterations):
            self.Log(Level.INFO, f"Instantiating NEST file (iteration {iteration})")
            try:
                sliceId = sliceManager.CreateSlice(nestData)
            except Exception as e:
                self.Log(Level.ERROR, f"Exception on instantiation, skipping iteration: {e}")
                sleep(pollTime)
                continue

            self.Log(Level.INFO, f"Slice ID: {sliceId}. Waiting for 'Running' status")
            totalWait = 0
            while True:
                sleep(pollTime)
                totalWait += pollTime
                sliceInfo = {}
                status = '<SliceManager check error>'
                try:
                    sliceInfo = sliceManager.CheckSlice(sliceId)
                    status = sliceInfo['status']
                    self.Log(Level.DEBUG, f"Status: {status}")
                except Exception as e:
                    self.Log(Level.WARNING, f"Exception while checking slice status: {e}")

                if status != 'Running':
                    if timeout is not None and totalWait >= timeout:
                        self.Log(Level.WARNING, f"Reached timeout. Skipping iteration")
                        break
                else:
                    self.Log(Level.INFO, "Slice running, retrieving deployment time.")
                    try:
                        creation_time = sliceInfo.get("deployment_time")
                        # Calculate the NS deployment time
                        ns_depl_time = 0.0
                        for ns, ns_time in creation_time["NS_Deployment_Time"].items():
                            ns_depl_time += float(ns_time)
                        creation_time["NS_Deployment_Time"] = ns_depl_time
                        creation_time["_iteration_"] = iteration
                        self.Log(Level.INFO,
                                 f"Deployment time for slice {sliceId} (Iteration {iteration}): {ns_depl_time}")
                    except Exception as e:
                        self.Log(Level.ERROR, f"Exception while calculating deployment time, skipping iteration: {e}")
                        break

                    point = InfluxPoint(datetime.now(timezone.utc))
                    for key, value in creation_time.items():
                        point.Fields[key] = value
                    payload.Points.append(point)
                    self.Log(Level.DEBUG, f'Payload point: {point}')
                    break

            try:
                self.Log(Level.INFO, "Deleting slice.")
                sliceManager.DeleteSlice(sliceId)
                totalWait = 0
                while True:
                    sleep(pollTime)
                    totalWait += pollTime
                    info = sliceManager.CheckSlice(sliceId)
                    if info is None:
                        self.Log(Level.INFO, f"Slice correctly deleted.")
                        break
                    elif timeout is not None and totalWait >= timeout:
                        self.Log(Level.WARNING, f"Slice not deleted before configured timeout.")
                        break
                    else:
                        self.Log(Level.DEBUG, f"Waiting for slice deletion.")
            except Exception as e:
                self.Log(Level.ERROR, f"Exception while deleting slice: {e}")

        self.Log(Level.DEBUG, f"Payload: {payload}")
        self.Log(Level.INFO, f"Sending results to InfluxDb")
        try:
            InfluxDb.Send(payload)
        except Exception as e:
            self.Log(Level.ERROR, f"Exception while sending payload: {e}")
            if csvFile is None:
                self.Log(Level.INFO, "Forcing creation of CSV file")
                csvFile = join(self.parent.TempFolder, f"SliceCreationTime.csv")

        if csvFile is not None:
            self.Log(Level.INFO, f"Writing result to CSV file: {csvFile}")
            InfluxDb.PayloadToCsv(payload, csvFile)
            self.parent.GeneratedFiles.append(csvFile)


