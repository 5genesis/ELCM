from Scheduler import app
from Helper import Log


@app.route('/api/executor/<int:executor_id>/start', methods=['POST'])
def executorStart(executor_id: int):
    Log.I(f'{executor_id} start')
    return ''


@app.route('/api/executor/<int:executor_id>/stop', methods=['POST'])
def executorStop(executor_id: int):
    Log.I(f'{executor_id} stop')
    return ''
