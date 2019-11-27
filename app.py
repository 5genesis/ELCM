from Scheduler import app, config
from Status import ExecutionQueue


@app.shell_context_processor
def make_shell_context():
    return {'App': app, 'Config': config, 'Queue': ExecutionQueue}
