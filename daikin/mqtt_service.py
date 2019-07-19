import os
import logging
import json
from datetime import datetime
import paho.mqtt.client as mqtt
from daikin import (AC_MODE, FAN_MODE, DaikinController)
"""
# Full example configuration.yaml entry
climate:
  - platform: mqtt
    name: Living Room Heater
    send_if_off: false
    initial: 20
    availability_topic: 'livingroom/ac/online'

    modes:
      - 'off'
      - 'auto'
      - 'cool'
      - 'heat'
      - 'fan_only'
    swing_modes:
      - 'both'
      - 'vertical'
      - 'horizonal'
      - 'off'
    fan_modes:
      - 'high'
      - 'medium'
      - 'low'
    power_command_topic: 'livingroom/ac/powerful/set'
    mode_command_topic: 'livingroom/ac/mode/set'
    temperature_command_topic: 'livingroom/ac/temperature/set'
    fan_mode_command_topic: 'livingroom/ac/fan/set'
    swing_mode_command_topic: 'livingroom/ac/swing/set'
    max_temp: 30
    min_temp: 18
"""
logger = logging.getLogger(__name__)

MQTT_BROKER = os.environ.get('MQTT_BROKER', '10.245.52.187')
# MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_USER = os.environ.get('MQTT_USER', 'mqtt_user')
MQTT_PASS = os.environ.get('MQTT_PASS', 'mqtt_password')
MQTT_TOPIC_PREFIX = 'livingroom/ac/'
SET_TEMPERATURE_TOPIC = os.environ.get('SET_TEMPERATURE_TOPIC',
                                       'temperature/set')
SET_POWER_TOPIC = os.environ.get('SET_POWER_TOPIC', 'power/set')
SET_MODE_TOPIC = os.environ.get('SET_MODE_TOPIC', 'mode/set')
SET_FAN_TOPIC = os.environ.get('SET_FAN_TOPIC', 'fan/set')
SET_SWING_TOPIC = os.environ.get('SET_SWING_TOPIC', 'swing/set')

TOPICS_LIST_FILE = os.path.join(os.path.dirname(__file__), 'topics')


def create_mqtt_loop():
    client = mqtt.Client("P1")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log
    client.username_pw_set(username="mqtt_user", password="mqtt_password")
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe('{}#'.format(MQTT_TOPIC_PREFIX))
    logger.info('Connection to {} on port {} established at {} UTC'.format(
        MQTT_BROKER, 1883,
        datetime.utcnow().isoformat()))
    client.loop_forever()


def on_connect(client, userdata, flags, rc):
    logger.info('Connected {}'.format(str(rc)))
    client.subscribe('{}#'.format(MQTT_TOPIC_PREFIX))


def on_disconnect(client, userdata, rc):
    logger.warning('Disconnected: {}\n{}'.format(str(rc), str(client)))


def on_log(client, obj, level, string):
    print(string)


def get_control_topic(control):
    return '{}{}'.format(MQTT_TOPIC_PREFIX, control)


def on_message(client, userdata, msg):
    print('Message Received\ntopic: {}\npayload: {}'.format(
        msg.topic, msg.payload))

    if msg.topic not in MQTT_TOPICS:
        MQTT_TOPICS.append(msg.topic)
        with open(TOPICS_LIST_FILE, 'w') as topics:
            json.dump({'topics': sorted(MQTT_TOPICS)},
                      topics,
                      indent=4,
                      sort_keys=True)
            logger.info('Found new mqtt topic: {} and saved it to file'.format(
                msg.topic))

    if msg.topic == get_control_topic(SET_TEMPERATURE_TOPIC):
        set_temperature(msg.payload.decode('utf-8'))
    elif msg.topic == get_control_topic(SET_MODE_TOPIC):
        set_mode(msg.payload.decode('utf-8'))
    elif msg.topic == get_control_topic(SET_FAN_TOPIC):
        set_fan(msg.payload.decode('utf-8'))
    elif msg.topic == get_control_topic(SET_SWING_TOPIC):
        set_swing(msg.payload.decode('utf-8'))
    elif msg.topic == get_control_topic(SET_POWER_TOPIC):
        set_power(msg.payload.decode('utf-8'))
    else:
        logger.warning('Unknown message: {}: {}'.format(
            msg.topic, msg.payload))


def send_daikin_state(**values):
    controller = DaikinController()
    controller.update(**values)


def set_temperature(value):
    logger.info('setting temperature to {}'.format(value))
    try:
        degrees = int(float(value))
    except ValueError:
        pass

    send_daikin_state(temperature=degrees)


def set_mode(value):
    logger.info('setting power to {}'.format(value))
    ac_mode = {
        'auto': AC_MODE.AUTO,
        'dry': AC_MODE.DRY,
        'cool': AC_MODE.COOL,
        'heat': AC_MODE.HEAT,
        'fan_only': AC_MODE.FAN,
    }.get(value, AC_MODE.AUTO)

    send_daikin_state(ac_mode=ac_mode)


def set_fan(value):
    logger.info('setting fan to {}'.format(value))
    fan = {
        'auto': FAN_MODE.AUTO,
        'low': FAN_MODE.ONE,
        'medium': FAN_MODE.THREE,
        'high': FAN_MODE.FIVE,
    }.get(value, FAN_MODE.AUTO)

    send_daikin_state(fan_mode=fan)


def set_swing(value):
    logger.info('setting swing mode to {}'.format(value))
    vertical = value in ['both', 'vertical']
    horizontal = value in ['both', 'horizontal']
    send_daikin_state(swing_vertical=vertical, swing_horizontal=horizontal)


def set_power(value):
    logger.info('setting power to {}'.format(value))
    power = value.lower() == 'on'
    send_daikin_state(power=power)


if __name__ == '__main__':
    logger = logging.getLogger('daikin-pi-mqtt-service')
    logger.setLevel(logging.INFO)
    logging.basicConfig()
    logger.info('MQTT Service Started')

    with open(TOPICS_LIST_FILE) as topics_file:
        MQTT_TOPICS = json.load(topics_file)['topics']

    create_mqtt_loop()
