from Helper import Log, Level
import threading


class Child:
    def __init__(self, name: str):
        self.name = name
        self.thread = threading.Thread(
            target=self.Run,
            daemon=True
        )

    def Say(self, level: Level, msg: str):
        Log.Log(level, f'[{self.name}{self.thread.ident}] {msg}')

    def Start(self):
        self.thread.start()

    def Run(self):
        raise NotImplementedError()
