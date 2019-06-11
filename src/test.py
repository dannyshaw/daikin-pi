from daikin import DaikinMessage, DaikinState, DaikinLIRC, AC_MODE, FAN_MODE


def main():
    state = DaikinState(power=True, temperature=25, ac_mode=AC_MODE.HEAT)
    state.fan_mode = FAN_MODE.FIVE
    message = DaikinMessage(state)

    lirc = DaikinLIRC()

    config = lirc.get_config(message)
    lirc.transmit(config)


if __name__ == '__main__':
    main()
