from Scheduler.facility import bp
from Facility import Facility
from flask import jsonify
from typing import Dict


@bp.route('/resource_status')
def resourceStatus():
    busy = Facility.BusyResources()
    idle = Facility.IdleResources()
    busyIds = [res.Id for res in busy]
    idleIds = [res.Id for res in idle]

    return jsonify({'Busy': busyIds, 'Idle': idleIds})


@bp.route('/ues')
def facilityUes():
    return jsonify({
        'UEs': sorted(list(Facility.ues.keys()))
    })


@bp.route('/testcases')
def facilityTestCases():
    res = []
    testcases = sorted(list(Facility.testCases.keys()))
    for testcase in testcases:
        data = Facility.GetTestCaseExtra(testcase)
        parametersDict: Dict[str, Dict[str, str]] = data.pop('Parameters', {})
        parameters = []
        data['Name'] = testcase
        for key in sorted(parametersDict.keys()):
            info = parametersDict[key]
            info['Name'] = key
            parameters.append(info)
        data['Parameters'] = parameters
        res.append(data)

    return jsonify({'TestCases': res})
