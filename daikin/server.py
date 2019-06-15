#!/usr/bin/python3.6

from .daikin import DaikinMessage, DaikinState, DaikinLIRC, AC_MODE
import json
from flask import Flask, request, jsonify
app = Flask(__name__)
CONFIG_FILE_NAME = '../data/config.json'


def save(state):
    with open(CONFIG_FILE_NAME, 'w') as f:
        json.dump(state.serialize(), f)


def load(data):
    with open(CONFIG_FILE_NAME, 'r') as f:
        data = json.load(f)

    return DaikinState.deserialize(data) if data else DaikinState()


def transmit(state):
    # save each time so incremental changes can be restored
    save(state)
    message = DaikinMessage(state)
    lirc = DaikinLIRC()
    config = lirc.get_config(message)
    lirc.transmit(config)
    return 'OK'


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# Presets for Google Assistant
@app.route('/heat/<int:temperature>', methods=['POST'])
def heat(temperature):
    state = DaikinState(temperature=temperature, ac_mode=AC_MODE.HEAT)
    return transmit(state)


@app.route('/cool/<int:temperature>', methods=['POST'])
def cool(temperature):
    state = DaikinState(temperature=temperature, ac_mode=AC_MODE.COOL)
    return transmit(state)


@app.route('/morning', methods=['POST'])
def morning():
    state = DaikinState(temperature=21, ac_mode=AC_MODE.HEAT)
    state.powerful = True
    return transmit(state)


# State Machine Controls
@app.route('/power')
def get_power(value):
    state = load()
    return state.power


@app.route('/power/<string:value>', methods=['POST'])
def set_power(value):
    state = load()
    if value in ['off', 'on']:
        state.power = value == 'on'
        transmit(state)
    else:
        raise InvalidUsage('Invalid power setting')


# State Machine Controls
@app.route('/temperature')
def get_temperature():
    state = load()
    return state.temperature


@app.route('/temperature/<int:degrees>', methods=['POST'])
def set_temperature(degrees=None):
    state = load()
    state.temperature = degrees
    transmit(state)


@app.route('/temperature/increase', methods=['POST'])
def increase_temperature():
    state = load()
    state.temperature = state.temperature + 1
    transmit(state)


@app.route('/temperature/decrease', methods=['POST'])
def decrease_temperature():
    state = load()
    state.temperature = state.temperature - 1
    transmit(state)


@app.route('/ac_mode')
def get_ac_mode():
    state = load()
    return state.serialize()['ac_mode']


@app.route('/ac_mode/<string:value>', methods=['POST'])
def set_ac_mode(value):
    state = load()
    if value in DaikinState.AC_MODE:
        state.ac_mode = value
        transmit(state)
    else:
        raise InvalidUsage('Invalid mode setting')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
