from Scheduler import app
from Status import Status
from flask import render_template, flash, redirect, url_for


@app.route("/")
def hello():
    return render_template('index.html', executionId=Status.nextId, activeExecutors=Status.activeExecutors)


@app.route('/start')
def start():
    executorId, executor = Status.CreateExecutor()
    executor.Start()
    flash(f'Created executor {executorId}')
    return redirect(url_for('hello'))


@app.route('/cancel/<int:executorId>')
def cancel(executorId: int):
    Status.CancelExecutor(executorId)
    flash(f'Cancelled executor {executorId}')
    return redirect(url_for('hello'))
