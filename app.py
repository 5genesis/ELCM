from Scheduler import app, config
from Status import ExperimentQueue


@app.shell_context_processor
def make_shell_context():
    return {'App': app, 'Config': config, 'Queue': ExperimentQueue}
