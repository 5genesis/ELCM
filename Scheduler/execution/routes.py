from flask import redirect, url_for, flash, render_template, jsonify, send_from_directory
from Status import Status, ExecutionQueue
from Experiment import ExperimentRun, Tombstone
from Scheduler.execution import bp
from typing import Union, Optional
from Settings import Config
from os.path import join, isfile, abspath


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
    execution = executionOrTombstone(executionId)
    coarse = status = 'ERR'
    percent = 0
    messages = []
    if execution is not None:
        coarse = execution.CoarseStatus.name
        if isinstance(execution, Tombstone):
            status = "Not Running"
        else:
            status = execution.Status
            percent = execution.PerCent
            messages = execution.Messages
    return jsonify({
        'Coarse': coarse, 'Status': status,
        'PerCent': percent, 'Messages': messages
    })


def executionOrTombstone(executionId: int) -> Optional[Union[ExperimentRun, Tombstone]]:
    execution = ExecutionQueue.Find(executionId)
    if execution is None:
        try:
            execution = Tombstone(str(executionId))
        except:
            execution = None
    return execution


@bp.route('<int:executionId>/logs')
def logs(executionId: int):
    execution = executionOrTombstone(executionId)

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


@bp.route('<int:executionId>/peerId')
def peerId(executionId: int):
    execution = executionOrTombstone(executionId)

    return jsonify({
        'RemoteId': execution.RemoteId if execution is not None else None
    })


# Shared implementation with east_west.files
@bp.route('<int:executionId>/results')
def results(executionId: int):
    return handleExecutionResults(executionId)


def handleExecutionResults(executionId: int):
    execution = executionOrTombstone(executionId)
    if execution is not None:
        folder = abspath(Config().ResultsFolder)
        filename = f"{executionId}.zip"
        if isfile(join(folder, filename)):
            return send_from_directory(folder, filename, as_attachment=True)
        else:
            return f"No results for execution {executionId}", 404
    else:
        return f"Execution {executionId} not found", 404


@bp.route('<int:executionId>/descriptor')
def descriptor(executionId: int):
    execution = executionOrTombstone(executionId)

    if execution is not None:
        return jsonify(execution.JsonDescriptor)
    else:
        return f"Execution {executionId} not found", 404


@bp.route('nextExecutionId')
def nextExecutionId():
    return jsonify({'NextId': Status.PeekNextId()})
