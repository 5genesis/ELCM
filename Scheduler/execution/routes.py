from flask import redirect, url_for, flash, render_template, jsonify
from Status import Status, ExecutionQueue
from Experiment import ExperimentRun, Tombstone
from Scheduler.execution import bp


@bp.route('<int:executionId>/cancel')
def cancel(executionId: int):
    ExecutionQueue.Cancel(executionId)
    flash(f'Cancelled execution {executionId}', 'info')
    return redirect(url_for('index'))


@bp.route('<int:executionId>/delete')
def delete(executionId: int):
    ExecutionQueue.Delete(executionId)
    flash(f'Deleted execution {executionId}', 'info')
    return redirect(url_for('index'))


@bp.route('<int:executionId>')
def view(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    if execution is None:
        try:
            execution = Tombstone(str(executionId))
        except:
            flash(f'Execution {executionId} does not exist or is not within Scheduler context', 'danger')

    if execution is None:
        return redirect(url_for('index'))
    else:
        return render_template('execution.html', execution=execution)


@bp.route('<int:executionId>/json')
def json(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    coarse = status = 'ERR'
    percent = 0
    messages = []
    if execution is not None:
        coarse = execution.CoarseStatus.name
        status = execution.Status
        percent = execution.PerCent
        messages = execution.Messages
    return jsonify({
        'Coarse': coarse, 'Status': status,
        'PerCent': percent, 'Messages': messages
    })


@bp.route('<int:executionId>/logs')
def logs(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    if execution is None:
        try:
            execution = Tombstone(str(executionId))
        except:
            execution = None

    if execution is not None:
        status = "Success"
        preRun = execution.PreRunner.RetrieveLogInfo().Serialize()
        executor = execution.Executor.RetrieveLogInfo().Serialize()
        postRun = execution.PostRunner.RetrieveLogInfo().Serialize()
    else:
        status = "Not Found"
        preRun = executor = postRun = None
    return jsonify({
        "Status": status, "PreRun": preRun, "Executor": executor, "PostRun": postRun
    })


@bp.route('nextExecutionId')
def nextExecutionId():
    return jsonify({'NextId': Status.PeekNextId()})
