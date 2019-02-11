from flask import Flask
from Helper import Log
from Status import Status
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from Helper import Config
from .heartbeat import HeartBeat

app = Flask(__name__)
config = Config()
app.config.from_mapping(config.Flask)
bootstrap = Bootstrap(app)
moment = Moment(app)
Log.Initialize(app)
Status.Initialize()
HeartBeat.Initialize()

from Scheduler.experiment import bp as ExperimentBp
app.register_blueprint(ExperimentBp, url_prefix='/experiment')

from Scheduler import routes, rest_server
