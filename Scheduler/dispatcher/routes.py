from flask import redirect, url_for, flash, render_template, jsonify, request
from Status import Status, ExperimentQueue
from Experiment import Experiment
from Helper import Serialize
from Scheduler.dispatcher import bp


@bp.route('/run', methods=['POST'])
def start():
    keys = ['ExperimentId', 'User', 'Name']
    data = request.json
    valid, missing = Serialize.CheckKeys(data, *keys)
    if not valid:
        executionId = None
        success = False
        message = f'Missing data: {missing}'
    else:
        experiment, user, name = Serialize.Unroll(data, *keys)
        executionId = ExperimentQueue.Create(data).Id
        success = True
        message = f'Created execution {executionId} for experiment {name} (Id:{experiment}, User:{user}) '
    return jsonify({
        'ExecutionId': executionId,
        'Success': success,
        'Message': message
    })
