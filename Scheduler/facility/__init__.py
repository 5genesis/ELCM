from flask import Blueprint

bp = Blueprint('facility', __name__)

from Scheduler.facility import routes
