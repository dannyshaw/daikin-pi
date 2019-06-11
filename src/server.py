from flask import Flask
app = Flask(__name__)


@app.route('/on')
def hello_world():
    return 'Hello, World!'
