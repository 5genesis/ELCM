from flask import redirect, url_for, flash, render_template
from Status import Status, ExperimentQueue
from Scheduler.experiment import bp


@bp.route('/start')
def start():
    experimentId, experiment = Status.CreateExperiment()
    flash(f'Experiment {experimentId} created', 'info')
    return redirect(url_for('index'))


@bp.route('<int:experimentId>/cancel')
def cancel(experimentId: int):
    Status.CancelExperiment(experimentId)
    flash(f'Cancelled experiment {experimentId}', 'info')
    return redirect(url_for('index'))


@bp.route('<int:experimentId>/delete')
def delete(experimentId: int):
    Status.DeleteExperiment(experimentId)
    flash(f'Deleted executor {experimentId}', 'info')
    return redirect(url_for('index'))


@bp.route('<int:experimentId>')
def view(experimentId:int):
    experiment = ExperimentQueue.Find(experimentId)
    if experiment is None:
        flash(f'Experiment {experimentId} does not exist or is not within Scheduler context', 'danger')
        return redirect(url_for('index'))
    return render_template('experiment.html', experiment=experiment)
