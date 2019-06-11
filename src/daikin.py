from enum import Enum
import subprocess


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
        # relevant bit indicies
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

        # relevant bit indicies
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
        """
        Most relevant information is stored in this frame
        A number of methods are used to update the frame data from empty bytes
        to a complete message

        Initial fixed bits are set

        Boolean Logical OR is used to flip boolean data on from
        default off using different
        bits depending on where data needs to be stored
        byte = byte | 0x01 flips the last bit
        byte = byte | 0x02 flips the second last bit
        byte = byte | 0x04 flips the third last bit, etc

        In places where
        """

        # relevant bit indicies
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

        #  AC_MODE_POWER_TIMERS - encodes all three into one byte (two nybbles)
        # [ 0     0     0     0     1      0        0       0     ]
        # [(       ac_mode      ) fixed (set on)(set off)(pwr on) ]

        # Set AC_MODE
        self._set_first_nybble(frame, MODE_POWER_TIMERS,
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
        self._set_first_nybble(frame, FAN_SETTING, self.state.fan_mode.value)

        # Fan Swing
        self._set_second_nybble(frame, SWING_HORIZONTAL,
                                self.state.swing_horizontal)
        self._set_second_nybble(frame, SWING_VERTICAL,
                                self.state.swing_vertical)

        # Timer Delay - complicated encoding not really completely understood
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
            mins = self.state.timer_duration * 60
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

    def _set_first_nybble(self, frame, index, to):
        frame[index] = 0x0f & frame[index]  # null first 4 bytes
        frame[index] = (to << 4) | frame[index]  # fill first 4 bytes

    def _set_second_nybble(self, frame, index, to):
        frame[index] = frame[index] & 0xf0
        frame[index] = frame[index] | to


class DaikinLIRC:

    GPIO_PIN_TX = 22

    PULSE = 430
    ZERO_GAP = 430
    ONE_GAP = 1320

    # these are strings as they will be output to an LIRC conf (as microsecond commands)
    ZERO = f'{PULSE} {ZERO_GAP}'
    ONE = f'{PULSE} {ONE_GAP}'
    FRAME_HEADER = '3440 1720'
    SHORT_GAP = f'{PULSE} 25000'
    LONG_GAP = f'{PULSE} 35500'

    def _get_lsb_binary_string(self, frame):
        # convert to binary byte string and reverse it
        return "".join(['{0:08b}'.format(item)[::-1] for item in frame])

    def _get_frame_codes(self, frame):
        binary_frame = self._get_lsb_binary_string(frame)
        # swap binary digits for pulse codes as defined above
        return '\n        '.join([
            self.ONE if digit == '1' else self.ZERO for digit in binary_frame
        ])

    def get_config(self, message):
        frame_one = self._get_frame_codes(message.frame_one)
        frame_two = self._get_frame_codes(message.frame_two)
        frame_three = self._get_frame_codes(message.frame_three)

        return f"""begin remote
    name    daikin-pi
    flags   RAW_CODES
    eps     30
    aeps    100
    gap     34978
    begin raw_codes
        name dynamic-signal
        {self.ZERO}
        {self.ZERO}
        {self.ZERO}
        {self.ZERO}
        {self.ZERO}
        {self.SHORT_GAP}
        {self.FRAME_HEADER}
        {frame_one}
        {self.LONG_GAP}
        {self.FRAME_HEADER}
        {frame_two}
        {self.LONG_GAP}
        {self.FRAME_HEADER}
        {frame_three}
        {self.PULSE}
    end raw_codes
end remote
        """

    def transmit(self, config):

        with open('daikin-pi.lircd.conf', 'w') as config_file:
            config_file.write(config)

        subprocess.check_output(
            ['sudo', 'cp', './daikin-pi.lircd.conf', '/etc/lirc/lircd.conf.d/'])
        subprocess.check_output(['sudo', 'service', 'lircd', 'restart'])
        subprocess.check_output(
            ['irsend', 'SEND_ONCE', 'daikin-pi', 'dynamic-signal'])
