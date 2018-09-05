#!/usr/bin/env python3
from enum import Enum
from pyslinger import IR


class AC_MODE(Enum):
    AUTO = 0x0
    DRY = 0x2
    COOL = 0x3
    HEAT = 0x4
    FAN = 0x6


class FAN_MODE(Enum):
    AUTO = 0xa
    SILENT = 0xb

    # Speed is technically a separate frame
    # if manual, speed is relevant
    ONE = 0x3
    TWO = 0x4
    THREE = 0x5
    FOUR = 0x6
    FIVE = 0x7


# on = delay til unit turns on
# off = delay til unit turns off
# none = no timer
class TIMER_MODE(Enum):
    SET_ON = True
    SET_OFF = False
    SET_NONE = None


class InvalidSetting(Exception):
    pass


class DaikinState:
    def __init__(self,
                 power=False,
                 temperature=20,
                 ac_mode=AC_MODE.AUTO,
                 fan_mode=FAN_MODE.AUTO):

        self._power = power
        self._temperature = temperature
        self._ac_mode = ac_mode
        self._fan_mode = fan_mode

        self._swing_vertical = False
        self._swing_horizontal = False
        self._economy = False
        self._comfort = False
        self._powerful = False
        self._timer = None

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        self._power = bool(value)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if value < 18:
            value = 18
        if value > 30:
            value = 30

        self._temperature = value

    @property
    def ac_mode(self):
        return self._ac_mode

    @ac_mode.setter
    def ac_mode(self, value):
        if value not in AC_MODE:
            value = AC_MODE.AUTO

        self._ac_mode = value

    @property
    def fan_mode(self):
        return self._fan_mode

    @fan_mode.setter
    def fan_mode(self, value):
        if value not in FAN_MODE:
            value = FAN_MODE.AUTO

        self._fan_mode = value

    @property
    def swing_vertical(self):
        return self._swing_vertical

    @swing_vertical.setter
    def swing_vertical(self, value):
        self._swing_vertical = bool(value)

    @property
    def swing_horizontal(self):
        return self._swing_horizontal

    @swing_horizontal.setter
    def swing_horizontal(self, value):
        self._swing_horizontal = bool(value)

    @property
    def economy(self):
        return self._economy

    @economy.setter
    def economy(self, value):
        self._economy = bool(value)

    @property
    def powerful(self):
        return self._powerful

    @powerful.setter
    def powerful(self, value):
        self._powerful = bool(value)

    @property
    def comfort(self):
        return self._comfort

    @comfort.setter
    def comfort(self, value):
        self._comfort = bool(value)

    @property
    def timer(self):
        return self._timer

    @timer.setter
    def timer(self, value):
        # TODO: timer
        self._timer = value


class DaikinMessage:
    def __init__(self, state):
        self.state = state

    @property
    def frame_one(self):
        MESSAGE_ID = 4
        COMFORT = 6
        CHECKSUM = 7

        frame = self._create_frame()

        # Message ID
        frame[MESSAGE_ID] = 0xc5

        # Comfort mode
        if self.state.comfort:
            frame[COMFORT] = 0x10

        # Checksum
        frame[CHECKSUM] = self._checksum(frame)

        return frame

    @property
    def frame_two(self):
        MESSAGE_ID = 4
        CHECKSUM = 7

        frame = self._create_frame()

        # Message ID
        frame[MESSAGE_ID] = 0x42

        # Checksum
        frame[CHECKSUM] = self._checksum(frame)

        return frame

    @property
    def frame_three(self):
        MESSAGE_ID = 4
        MODE_POWER_TIMERS = 5
        TEMPERATURE = 6
        SWING_HORIZONTAL = 8
        FAN_SETTING = 8
        SWING_VERTICAL = 9
        TIMER_A = 10
        TIMER_B = 11
        TIMER_C = 12
        POWERFUL = 13
        ECONOMY = 16
        CHECKSUM = 18

        frame = self._create_frame(19)

        # Set initial fixed frame bits
        frame[SWING_HORIZONTAL] = 0xb0
        frame[MODE_POWER_TIMERS] = 0x08
        frame[15] = 0xc1  # dunno just always set to this..
        frame[ECONOMY] = 0x80

        # Message ID
        frame[MESSAGE_ID] = 0x00

        # Temperature - doubled for encoding
        frame[TEMPERATURE] = self.state.temperature << 1

        #  AC_MODE_POWER_TIMERS - encodes all three into one byte
        # [ 0     0     0     0     1      0        0       0     ]
        # [(       ac_mode      ) fixed (set on)(set off)(pwr on) ]

        # Set AC_MODE
        self._set_first_four_bits(frame, MODE_POWER_TIMERS,
                                  self.state.ac_mode.value)

        # Timer Is Setting Unit On/Off
        if self.state.timer is not None:
            if self.state.timer == TIMER_MODE.OFF:
                frame[MODE_POWER_TIMERS] = frame[MODE_POWER_TIMERS] | 0x04
            elif self.state.timer == TIMER_MODE.ON:
                frame[MODE_POWER_TIMERS] = frame[MODE_POWER_TIMERS] | 0x02

        # Power On/Off
        if self.state.power:
            frame[MODE_POWER_TIMERS] = frame[MODE_POWER_TIMERS] | 0x01

        # Fan Mode/Speed
        self._set_first_four_bits(frame, FAN_SETTING,
                                  self.state.fan_mode.value)

        # Fan Swing
        self._set_last_four_bits(frame, SWING_HORIZONTAL,
                                 self.state.swing_horizontal)
        self._set_last_four_bits(frame, SWING_VERTICAL,
                                 self.state.swing_vertical)

        # Timer Delay - complicated encoding
        # Timer ON sets duration at TIMER_A and TIMER_B
        # Timer OFF sets duration at TIMER_B and TIMER_C
        frame[TIMER_A] = 0x00
        frame[TIMER_B] = 0x00
        frame[TIMER_C] = 0x00

        if self.state.timer is None:
            frame[TIMER_B] = 0x06
            frame[TIMER_C] = 0x60

        # wat?
        frame[TIMER_B] = frame[TIMER_B] | 0x06
        frame[TIMER_C] = frame[TIMER_C] | 0x60

        if self.state.timer == TIMER_MODE.SET_OFF:
            mins = self.state.timer_duration * 60
            if mins > 0xff:
                frame[TIMER_C] = mins >> 8
                frame[TIMER_B] = mins & 0xff
            else:
                frame[TIMER_C] = mins >> 4
                frame[TIMER_B] = frame[TIMER_B] | (mins & 0x0f) << 4
        elif self.state.timer == TIMER_MODE.SET_ON:
            mins = state.timer_duration * 60
            frame[TIMER_A] = mins & 0xff
            frame[TIMER_B] = (mins >> 8) & 0xff

        # Powerful
        if self.state.powerful:
            frame[POWERFUL] = 0x01

        if self.state.economy:
            frame[ECONOMY] = frame[ECONOMY] | 0x04

        # Checksum
        frame[CHECKSUM] = self._checksum(frame)

        return frame

    def _create_frame(self, size=8):
        frame = [0x00 for _ in range(size)]
        # All frames start with this header
        frame[0] = 0x11
        frame[1] = 0xda
        frame[2] = 0x27
        frame[3] = 0x00
        return frame

    def _checksum(self, frame):
        return sum(frame) & 0xff

    def _set_first_four_bits(self, frame, index, to):
        frame[index] = 0x0f & frame[index]  # null first 4 bytes
        frame[index] = (to << 4) | frame[index]  # fill first 4 bytes

    def _set_last_four_bits(self, frame, index, to):
        frame[index] = frame[index] & 0xf0
        frame[index] = frame[index] | to


class DaikinIR:
    def __init__(self):

        protocol = "NEC"
        gpio_pin = 25
        protocol_config = dict({
            'duty_cycle': 0.33,
            'leading_pulse_duration': 3400,
            'leading_gap_duration': 1750,
            'one_pulse_duration': 430,
            'one_gap_duration': 420,
            'zero_pulse_duration': 430,
            'zero_gap_duration': 1320,
            'trailing_pulse': 1,
        })
        self.ir = IR(gpio_pin, protocol, protocol_config)

        self.state = DaikinState()
        self.message = DaikinMessage(self.state)

    def frame_bin(self, frame):
        return "".join([bin(item)[2:].zfill(8) for item in frame])

    def transmit(self):
        self.state.power = True

        # code = self.frame_bin(self.message.frame_one + self.message.frame_two +
        #                       self.message.frame_three)
        # print(self.message.frame_one)
        # print(self.message.frame_two)
        # print(self.message.frame_three)
        from time import sleep
        self.ir.send_code(
            self.frame_bin(self.message.frame_one) +
            self.frame_bin(self.message.frame_two) +
            self.frame_bin(self.message.frame_three))
        # self.send_code(self.frame_bin(self.message.frame_three[8:16]))
        # self.send_code(self.frame_bin(self.message.frame_three[16:]))


if __name__ == "__main__":
    daikin = DaikinIR()
    daikin.transmit()
    print("Exiting IR")
