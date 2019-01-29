from Scheduler import app
from Status import Status
from flask import render_template


@app.route("/")
def hello():
    return render_template('index.html', executionId=Status.nextId, activeExecutors=Status.activeExecutors)


@app.route('/start')
def start():
    executorId, executor = Status.CreateExecutor()
    executor.Start()
    return f'Created executor {executorId}'


