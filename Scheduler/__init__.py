from flask import Flask
from Helper import Log
from Status import Status
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from Helper import Config


app = Flask(__name__)
config = Config()
app.config.from_mapping(config.Flask)
bootstrap = Bootstrap(app)
moment = Moment(app)
Log.Initialize(app)
Status.Initialize()

from Scheduler import routes, rest_server
