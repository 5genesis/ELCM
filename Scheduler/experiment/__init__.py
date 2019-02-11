from flask import Blueprint

bp = Blueprint('experiment', __name__)

from Scheduler.experiment import routes