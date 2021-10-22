from flask import Flask
from Helper import Log
from Status import Status
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from Settings import Config, EvolvedConfig
from Facility import Facility
from .heartbeat import HeartBeat
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='./.flaskenv', verbose=True)

def _showValidation(name, validation):
    print(f"{name} validation:")
    for level, message in validation:
        print(f"  {level.name:8}: {message}", flush=True)


config = Config()
_showValidation("Config", config.Validation)

evolvedConfig = EvolvedConfig()
_showValidation("Evolved5g Config", evolvedConfig.Validation)

Facility.Reload()
_showValidation("Facility", Facility.Validation)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

bootstrap = Bootstrap(app)
moment = Moment(app)
Log.Initialize(app)
Status.Initialize()
HeartBeat.Initialize()

from Scheduler.execution import bp as ExecutionBp
app.register_blueprint(ExecutionBp, url_prefix='/execution')

from Scheduler.dispatcher import bp as DispatcherBp
app.register_blueprint(DispatcherBp, url_prefix='/api/v0')

from Scheduler.facility import bp as FacilityBp
app.register_blueprint(FacilityBp, url_prefix='/facility')

if config.EastWest.Enabled:
    from Scheduler.east_west import bp as EastwestBp
    app.register_blueprint(EastwestBp, url_prefix='/distributed')

Log.I(f'Optional East/West interface is {Log.State(config.EastWest.Enabled)}')

from Scheduler import routes
