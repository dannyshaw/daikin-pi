from unittest import TestCase
from mock import patch, MagicMock

from daikin.mqtt_service import (
    set_mode,
    set_fan,
    set_temperature,
    set_swing,
)

from daikin.daikin import AC_MODE, FAN_MODE, DaikinController


@patch('daikin.mqtt_service.DaikinController')
class TestMQTTDaikinSetters(TestCase):
    def test_set_temperature(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock
        set_temperature(20)
        dmock.update.assert_called_with(temperature=20)
        set_temperature(18)
        dmock.update.assert_called_with(temperature=18)
        set_temperature(30)
        dmock.update.assert_called_with(temperature=30)

    def test_set_power(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock

        set_power('on')
        dmock.update.assert_called_with(power=True)
        set_power('off')
        dmock.update.assert_called_with(power=False)

    def test_set_mode(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock

        set_mode('auto')
        dmock.update.assert_called_with(ac_mode=AC_MODE.AUTO)
        set_mode('cool')
        dmock.update.assert_called_with(ac_mode=AC_MODE.COOL)
        set_mode('heat')
        dmock.update.assert_called_with(ac_mode=AC_MODE.HEAT)
        set_mode('fan_only')
        dmock.update.assert_called_with(ac_mode=AC_MODE.FAN)
        set_mode('dry')
        dmock.update.assert_called_with(ac_mode=AC_MODE.DRY)

    def test_set_fan(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock
        set_fan('auto')
        dmock.update.assert_called_with(fan_mode=FAN_MODE.AUTO)
        set_fan('low')
        dmock.update.assert_called_with(fan_mode=FAN_MODE.ONE)
        set_fan('medium')
        dmock.update.assert_called_with(fan_mode=FAN_MODE.THREE)
        set_fan('high')
        dmock.update.assert_called_with(fan_mode=FAN_MODE.FIVE)

    def test_set_swing(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock

        set_swing('both')
        dmock.update.assert_called_with(swing_vertical=True,
                                        swing_horizontal=True)
        set_swing('vertical'),
        dmock.update.assert_called_with(swing_vertical=True,
                                        swing_horizontal=False)
        set_swing('horizontal'),
        dmock.update.assert_called_with(swing_vertical=False,
                                        swing_horizontal=True)
        set_swing('off'),
        dmock.update.assert_called_with(swing_vertical=False,
                                        swing_horizontal=False)
