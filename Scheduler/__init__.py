from flask import Flask
from Helper import Log
from Status import Status


app = Flask(__name__)
Log.Initialize(app)
Status.Initialize()

from Scheduler import routes, rest_server
