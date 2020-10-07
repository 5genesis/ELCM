from Scheduler.east_west import bp
from flask import jsonify
from Status import ExecutionQueue


notFound = jsonify({'success': False, 'status': None, 'milestones': [],
                    'message': 'Execution ID is not valid or experiment is not running'})


@bp.route('/<int:executionId>/status')
def status(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    if execution is not None:
        return jsonify({'success': True, 'status': execution.Status, 'milestones': execution.Milestones,
                        'message': f'Status of execution {executionId} retrieved successfully'})
    else:
        return notFound


@bp.route('/<int:executionId>/values')
@bp.route('/<int:executionId>/values/<name>')
def values(executionId: int, name: str = None):
    execution = ExecutionQueue.Find(executionId)
    if execution is not None:
        return "PENDING"
    else:
        return notFound


@bp.route('/<int:executionId>/results')
def results(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    if execution is not None:
        return "PENDING"
    else:
        return notFound