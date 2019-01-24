from flask import Flask
from Helper import Log


app = Flask(__name__)
Log.Initialize(app)


@app.route('/')
def hello_world():
    Log.D("aajskdjhsahdfalkhfhaf")
    return 'Hello World!'
