from Task import Task
from Helper import Level
from time import sleep


class Delay(Task):
    def __init__(self, logMethod, parent, params):
        super().__init__("Message", parent, params, logMethod, None)

    def Run(self):
        value = self.params.get('Time', 60)
        try:
            time = int(value)
            if time < 0:
                raise ValueError
        except ValueError:
            self.Log(Level.ERROR, f"{value} is not a valid number of seconds")
            return

        self.Log(Level.INFO, f'Waiting for {time} seconds')
        sleep(time)
