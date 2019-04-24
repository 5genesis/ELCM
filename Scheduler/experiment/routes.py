from flask import redirect, url_for, flash, render_template, jsonify
from Status import Status, ExperimentQueue
from Experiment import ExperimentRun, Tombstone
from Scheduler.experiment import bp


@bp.route('/start')
def start():
    params = {'User': {'UserName': 'LocalAdmin'}, 'ExperimentId': -1, 'Name': 'LocalTest'}
    experiment = ExperimentQueue.Create(params)
    flash(f'Experiment {experiment.Id} created', 'info')
    return redirect(url_for('index'))


@bp.route('<int:experimentId>/cancel')
def cancel(experimentId: int):
    ExperimentQueue.Cancel(experimentId)
    flash(f'Cancelled experiment {experimentId}', 'info')
    return redirect(url_for('index'))


@bp.route('<int:experimentId>/delete')
def delete(experimentId: int):
    ExperimentQueue.Delete(experimentId)
    flash(f'Deleted executor {experimentId}', 'info')
    return redirect(url_for('index'))


@bp.route('<int:experimentId>')
def view(experimentId: int):
    experiment = ExperimentQueue.Find(experimentId)
    if experiment is None:
        try:
            experiment = Tombstone(str(experimentId))
        except:
            flash(f'Experiment {experimentId} does not exist or is not within Scheduler context', 'danger')
    if experiment is None:
        return redirect(url_for('index'))
    else:
        return render_template('experiment.html', experiment=experiment)


@bp.route('<int:experimentId>/json')
def json(experimentId: int):
    experiment = ExperimentQueue.Find(experimentId)
    coarse = status = 'ERR'
    percent = 0
    messages = []
    if experiment is not None:
        coarse = experiment.CoarseStatus.name
        status = experiment.Status
        percent = experiment.PerCent
        messages = experiment.Messages
    return jsonify({
        'Coarse': coarse, 'Status': status,
        'PerCent': percent, 'Messages': messages
    })


@bp.route('nextExperimentId')
def nextExperimentId():
    return jsonify({'NextId': Status.PeekNextId()})
