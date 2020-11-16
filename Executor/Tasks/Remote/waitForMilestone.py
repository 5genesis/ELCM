from .base_remote_task import BaseRemoteTask
from Helper import Level
from time import sleep
from Executor import ExecutorStatus


class WaitForMilestone(BaseRemoteTask):
    def __init__(self, logMethod, parent, params):
        super().__init__("Wait for Milestone", logMethod, parent, params)

    def Run(self):
        milestone = self.params.get('Milestone', None)

        if milestone is None:
            self.Log(Level.ERROR, "'Milestone' not defined, please review the Task configuration.")
            return

        milestones = []
        while milestone not in milestones:
            self.Log(Level.DEBUG,
                     f"Trying to retrieve experiment status from remote. Timeout in {self.timeout} seconds.")
            status, milestones = self.remoteApi.GetStatus(self.remoteId)
            self.Log(Level.DEBUG, f"Status: '{status}'; Milestones: {milestones}")

            if status in [ExecutorStatus.Cancelled, ExecutorStatus.Errored]:
                raise RuntimeError(f"Execution on remote side has been terminated with status: {status.name}")

            if milestone not in milestones:
                if self.timeout <= 0:
                    raise RuntimeError(f"Timeout reached while waiting for milestone '{milestone}'.")
                sleep(5)
                self.timeout -= 5

        self.Log(Level.INFO, f"Remote side reached milestone '{milestone}'.")
