from daikin.daikin import DaikinMessage, DaikinState, DaikinLIRC, AC_MODE, FAN_MODE
import json

CONFIG_FILE_NAME = '../data/config.json'


def save(state):
    with open(CONFIG_FILE_NAME, 'w') as f:
        json.dump(state.serialize(), f)


def load():
    with open(CONFIG_FILE_NAME, 'r') as f:
        data = json.load(f)

    return DaikinState.deserialize(data) if data else DaikinState()


class daikin_machine(object):
    def __init__(self):
        self.state = 'one'

    def __enter__(self):
        return self.state

    def __exit__(self, type, value, traceback):
        print(self.state)
        print(value)
        print(type)
        print(traceback)


def main():
    state = DaikinState(power=True, temperature=29, ac_mode=AC_MODE.HEAT)
    state.fan_mode = FAN_MODE.FIVE

    state = load()

    with daikin_machine() as blah:
        blah = 'two'
    # print(state.serialize())


def test_template():
    state = DaikinState(power=True, temperature=29, ac_mode=AC_MODE.HEAT)
    message = DaikinMessage(state)
    lirc = DaikinLIRC()

    config = lirc.get_config(message)
    print(config)


if __name__ == '__main__':
    test_template()
    # main()
