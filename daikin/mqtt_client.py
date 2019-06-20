import paho.mqtt.client as mqtt

# from .daikin import (
#     AC_MODE,
#     FAN_MODE,
# )


def on_message(client, user_data, message):
    import ipdb
    ipdb.set_trace()
    print(message.topic)


import time
client = mqtt.Client("P1")  #create new instance
client.connect('localhost')  #connect to broker
client.loop_start()
client.subscribe('topic')
client.on_message = on_message
time.sleep(4)
