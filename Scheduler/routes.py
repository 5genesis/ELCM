from Scheduler import app
from Status import Status


@app.route("/")
def hello():
    return str(Status.nextId)
