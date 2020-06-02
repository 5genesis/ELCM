from flask import jsonify, request
from Status import ExecutionQueue
from Data import ExperimentDescriptor
from Scheduler.dispatcher import bp
from Helper import Log


@bp.route('/run', methods=['POST'])
def start():
    data = request.json
    Log.I("Received execution request")
    Log.D(f"Payload: {data}")
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
        message = f'Created execution {executionId}'

    response = {
        'ExecutionId': executionId,
        'Success': success,
        'Message': message
    }

    Log.D(f"Response: {response}")
    return jsonify(response)
