from Scheduler import app
from Status import Status


@app.route("/")
def hello():
    return str(Status.nextId)


@app.route('/start')
def start():
    executorId, executor = Status.CreateExecutor()
    executor.Start()
    return f'Created executor {executorId}'


