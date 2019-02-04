from flask import redirect, url_for, flash, render_template
from Status import Status, ExperimentQueue
from Executor import ExecutorStatus
from Scheduler.executor import bp
from Interfaces import Management


@bp.route('/start')
def start():
    executorId, executor = Status.CreateExecutor()
    hasResources = Management.HasResources(executor)
    if hasResources:
        executor.Start()
        flash(f'Started executor {executorId}', 'info')
    else:
        executor.Status = ExecutorStatus.Waiting
        flash(f'Executor {executorId} waiting', 'warning')
    return redirect(url_for('index'))


@bp.route('<int:executorId>/cancel')
def cancel(executorId: int):
    Status.CancelExecutor(executorId)
    flash(f'Cancelled executor {executorId}', 'info')
    return redirect(url_for('index'))


@bp.route('<int:executorId>/delete')
def delete(executorId: int):
    try:
        executor = ExperimentQueue.Find(executorId)
        if executor.Status != ExecutorStatus.Running:
            executor.Save()
            Status.DeleteExecutor(executorId)
            flash(f'Deleted executor {executorId}', 'info')
        else:
            flash(f'Cannot remove {executorId}', 'danger')
    except Exception as e:
        flash(f'Exception while deleting executor {executorId}', 'danger')

    return redirect(url_for('index'))


@bp.route('<int:executorId>')
def view(executorId:int):
    executor = ExperimentQueue.Find(executorId)
    if executor is None:
        flash(f'Executor {executorId} does not exist or is not within Scheduler context', 'danger')
        return redirect(url_for('index'))
    return render_template('executor.html', executor=executor)
