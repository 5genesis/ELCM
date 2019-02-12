from Scheduler import app
from Status import Status, ExperimentQueue
from Experiment import Experiment
from flask import render_template, make_response, request
from functools import wraps, update_wrapper
from datetime import datetime
from Helper import Log, Serialize
from typing import List, Dict
from flask_paginate import Pagination, get_page_parameter


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


@app.route("/history")
def history():
    experiments: List[Dict] = []
    ids = Serialize.List(False, False, 'Experiment')
    for id in reversed(sorted(ids)):
        digest = Experiment.Load(id)
        experiments.append(digest)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=len(experiments), search=False,
                            record_name='experiments', per_page=10, bs_version=4,
                            display_msg='Displaying <b>{start} - {end}</b> {record_name} (out of <b>{total}</b>)')
    start = pagination.skip
    end = start + pagination.per_page
    experiments = experiments[start:end]
    return render_template('history.html', experiments=experiments, pagination=pagination)
