from flask import jsonify, request
from Status import ExecutionQueue
from Data import ExperimentDescriptor
from Scheduler.dispatcher import bp


@bp.route('/run', methods=['POST'])
def start():
    data = request.json
    descriptor = ExperimentDescriptor(data)
    valid, reasons = descriptor.ValidityCheck
    if not valid:
        executionId = None
        success = False
        message = f'Invalid experiment description: {"; ".join(reasons)}'
    else:
        params = {'Descriptor': descriptor}
        executionId = ExecutionQueue.Create(params).Id
        success = True
        message = f'Created execution {executionId} for experiment {descriptor.Name} ' \
            f'(Id:{descriptor.Id}, User:{descriptor.User.Name})'
    return jsonify({
        'ExecutionId': executionId,
        'Success': success,
        'Message': message
    })
