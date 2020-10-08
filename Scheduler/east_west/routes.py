from Scheduler.east_west import bp
from flask import jsonify, request, json
from Status import ExecutionQueue


notFound = {'success': False, 'message': 'Execution ID is not valid or experiment is not running'}
hiddenVariables = ['Configuration', 'Descriptor']


@bp.route('/<int:executionId>/peerDetails', methods=['POST'])
def peer(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    if execution is not None:
        data = request.json
        try:
            host = data['host']
            port = data['port']
            execId = data['execution_id']
        except KeyError as e:
            return jsonify({'success': False, 'message': f'Invalid payload: {e}'})
        return "PENDING"
    else:
        return jsonify(notFound)


@bp.route('/<int:executionId>/status')
def status(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    if execution is not None:
        return jsonify({'success': True, 'status': execution.Status, 'milestones': execution.Milestones,
                        'message': f'Status of execution {executionId} retrieved successfully'})
    else:
        return jsonify(notFound)


@bp.route('/<int:executionId>/values')
@bp.route('/<int:executionId>/values/<name>')
def values(executionId: int, name: str = None):
    execution = ExecutionQueue.Find(executionId)
    if execution is not None:
        variables = {}
        for key, value in execution.Params.items():
            if key not in hiddenVariables:
                variables[str(key)] = str(value)
        if name is None:
            return jsonify({'success': True, 'values': variables,
                            'message': f'Variables of execution {executionId} retrieved successfully'})
        else:
            if name in variables.keys():
                return jsonify({'success': True, 'value': variables[name],
                                'message': f"Value of '{name}' for execution {executionId} retrieved successfully"})
            else:
                return jsonify({'success': False,
                                'message': f"Value of '{name}' is not available for execution {executionId}"})
    else:
        return jsonify(notFound)


@bp.route('/<int:executionId>/results')
def results(executionId: int):
    execution = ExecutionQueue.Find(executionId)
    if execution is not None:
        return "PENDING"
    else:
        return jsonify(notFound)
