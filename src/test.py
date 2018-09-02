from .daikin import DaikinState, DaikinMessage
from .pyslinger import IR


class DaikinIR:
    def __init__(self):
        protocol = "NEC"
        gpio_pin = 25
        protocol_config = dict()
        self.ir = IR(gpio_pin, protocol, protocol_config)
        self.state = DaikinState()
        self.message = DaikinMessage(self.state)

    def transmit(self):
        self.state.power = True

        ir.send_code(self.message.frame_one)
        ir.send_code(self.message.frame_two)
        ir.send_code(self.message.frame_three)


if __name__ == "__main__":
    daikin = DaikinIR()
    daikin.transmit()
    print("Exiting IR")
