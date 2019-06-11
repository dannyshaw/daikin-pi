#!/usr/bin/python3
from .daikin import DaikinMessage, DaikinState, DaikinLIRC, AC_MODE, FAN_MODE
from flask import Flask
app = Flask(__name__)



def main():
    state = DaikinState(power=True, temperature=20, ac_mode=AC_MODE.HEAT)
    state.fan_mode = FAN_MODE.AUTO
    state.powerful = True

    message = DaikinMessage(state)

    lirc = DaikinLIRC()

    config = lirc.get_config(message)
    lirc.transmit(config)
    return "OK"

@app.route('/morning')
def hello_world():
    return main() 

if __name__ == '__main__':
    main()
