from Scheduler import app
from Status import Status, ExperimentQueue
from flask import render_template, flash, redirect, url_for, make_response
from functools import wraps, update_wrapper
from datetime import datetime
from Helper import Log


# https://arusahni.net/blog/2014/03/flask-nocache.html
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache, view)


@app.route("/")
@nocache
def index():
    return render_template('index.html', executionId=Status.nextId, experiments=ExperimentQueue.Retrieve())


@app.route("/log")
def log():
    return render_template('mainLog.html', logInfo=Log.RetrieveLogInfo(tail=100))
