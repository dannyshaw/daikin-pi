#!/usr/bin/python3
from .daikin import DaikinMessage, DaikinState, DaikinLIRC, AC_MODE, FAN_MODE
from flask import Flask
app = Flask(__name__)


def transmit(state):
    message = DaikinMessage(state)
    lirc = DaikinLIRC()
    config = lirc.get_config(message)
    lirc.transmit(config)
    return 'OK'


@app.route('/heat/<int:temperature>', methods=['POST'])
def heat(temperature):
    state = DaikinState(
        power=True, temperature=temperature, ac_mode=AC_MODE.HEAT)
    state.fan_mode = FAN_MODE.AUTO
    return transmit(state)


@app.route('/cool/<int:temperature>', methods=['POST'])
def cool(temperature):
    state = DaikinState(
        power=True, temperature=temperature, ac_mode=AC_MODE.COOL)
    state.fan_mode = FAN_MODE.AUTO
    return transmit(state)


@app.route('/morning', methods=['POST'])
def cool(temperature):
    state = DaikinState(power=True, temperature=21, ac_mode=AC_MODE.HEAT)
    state.fan_mode = FAN_MODE.AUTO
    state.powerful = True
    return transmit(state)
