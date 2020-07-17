from Scheduler.facility import bp
from Facility import Facility
from Interfaces import Management
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
        if testcase == 'MONROE_Base': continue

        # Work over a copy, otherwise we end up overwriting the Facility data
        extra = Facility.GetTestCaseExtra(testcase).copy()
        parametersDict: Dict[str, Dict[str, str]] = extra.pop('Parameters', {})
        parameters = []
        extra['Name'] = testcase
        for key in sorted(parametersDict.keys()):
            info = parametersDict[key]
            info['Name'] = key
            parameters.append(info)
        extra['Parameters'] = parameters
        res.append(extra)

    return jsonify({'TestCases': res})


@bp.route('/baseSliceDescriptors')
def baseSliceDescriptors():
    sliceManager = Management.SliceManager()
    return jsonify(sliceManager.GetBaseSliceDescriptors())


@bp.route('/scenarios')
def scenarios():
    return jsonify({"Scenarios": list(Facility.scenarios.keys())})
