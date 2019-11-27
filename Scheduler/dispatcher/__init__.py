from flask import Blueprint

bp = Blueprint('dispatcherApi', __name__)

from Scheduler.dispatcher import routes
