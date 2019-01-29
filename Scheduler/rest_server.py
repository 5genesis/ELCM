from Scheduler import app
from Status import Status


@app.route('/api/executor/<int:executor_id>/start', methods=['POST'])
def executorStart(executor_id: int):
    print(f'{executor_id} start')
    return ''


@app.route('/api/executor/<int:executor_id>/stop', methods=['POST'])
def executorStop(executor_id: int):
    print(f'{executor_id} stop')
    #Status.DeleteExecutor(executor_id)
    return ''
