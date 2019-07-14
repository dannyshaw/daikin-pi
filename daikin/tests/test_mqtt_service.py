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
        dmock.set_temperature.assert_called_with(20)
        set_temperature(18)
        dmock.set_temperature.assert_called_with(18)
        set_temperature(30)
        dmock.set_temperature.assert_called_with(30)

    def test_set_mode(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock

        set_mode('auto')
        dmock.set_mode.assert_called_with(AC_MODE.AUTO)
        set_mode('cool')
        dmock.set_mode.assert_called_with(AC_MODE.COOL)
        set_mode('heat')
        dmock.set_mode.assert_called_with(AC_MODE.HEAT)
        set_mode('fan')
        dmock.set_mode.assert_called_with(AC_MODE.FAN)
        set_mode('dry')
        dmock.set_mode.assert_called_with(AC_MODE.DRY)

    def test_set_fan(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock
        set_fan('auto')
        dmock.set_fan.assert_called_with(FAN_MODE.AUTO)
        set_fan('low')
        dmock.set_fan.assert_called_with(FAN_MODE.ONE)
        set_fan('medium')
        dmock.set_fan.assert_called_with(FAN_MODE.THREE)
        set_fan('high')
        dmock.set_fan.assert_called_with(FAN_MODE.FIVE)

    def test_set_swing(self, daikin):
        dmock = MagicMock(spec=DaikinController)
        daikin.return_value = dmock

        set_swing('both')
        dmock.set_swing.assert_called_with(vertical=True, horizontal=True)
        set_swing('vertical'),
        dmock.set_swing.assert_called_with(vertical=True, horizontal=False)
        set_swing('horizontal'),
        dmock.set_swing.assert_called_with(vertical=False, horizontal=True)
        set_swing('off'),
        dmock.set_swing.assert_called_with(vertical=False, horizontal=False)
