from flask import Blueprint

bp = Blueprint('executor', __name__)

from Scheduler.executor import routes