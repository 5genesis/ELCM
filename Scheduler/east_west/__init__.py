from flask import Blueprint

bp = Blueprint('eastWest', __name__)

from Scheduler.east_west import routes
