from flask import Flask
from Helper import Log
from Executor import Executor

app = Flask(__name__)
Log.Initialize(app)


@app.route('/')
def hello_world():
    e = Executor({'id': 'hfhfhf'})
    e.Start()

    return 'Hello World!'
