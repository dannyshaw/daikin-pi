# Raspberry Pi IR Gateway for Daikin ARC remote control

Tested on my split system which uses a remote with the model number `ARC433B70`

## Installation

### Configure LIRC

Assumes the use of gpio pin 22 for tx, 23 for rx, edit accordingly.

Install LIRC
```
$ sudo apt install lirc
```

Ensure this line in /boot/config.txt:
```
dtoverlay=lirc-rpi,gpio_in_pin=23,gpio_out_pin=22,gpio_in_pull=up
```

Edit or create /etc/lirc/hardware.conf
```
########################################################
# /etc/lirc/hardware.conf
#
# Arguments which will be used when launching lircd
LIRCD_ARGS="--uinput"
# Don't start lircmd even if there seems to be a good config file
# START_LIRCMD=false
# Don't start irexec, even if a good config file seems to exist.
# START_IREXEC=false
# Try to load appropriate kernel modules
LOAD_MODULES=true
# Run "lircd --driver=help" for a list of supported drivers.
DRIVER="default"
# usually /dev/lirc0 is the correct setting for systems using udev
DEVICE="/dev/lirc0"
MODULES="lirc_rpi"
# Default configuration files for your hardware if any
LIRCD_CONF=""
LIRCMD_CONF=""
########################################################
```

Add these lines to /etc/modules
```
lirc_dev
lirc_rpi gpio_in_pin=23 gpio_out_pin=22
```

Reboot

### Test LIRC Circuit with a simple IR signal to test it works

Find a remote for your tv or something here or elsewhere on the web
http://lirc.sourceforge.net/remotes/

Copy it to
`/etc/lirc/lircd.conf.d/<remote-name>.lircd.conf`

Restart lirc
`sudo systemctl restart lircd`

Send a command to the remote
`sudo irsend SEND_ONCE <remote-name> <command-name>`

eg, `sudo irsend SEND_ONCE SamsungTV KEY_POWER`
To turn on the tv...


### Send a Daikin remote command

In the root folder there is a file called `daikin.lircd.conf`
This is a valid single command for my Daikin. It should set it to heat (20 degrees from memory)
Test that it works by firing this command at your Daikin

```
# install the file
sudo sp daikin-pi.lircd.conf /etc/lirc/lircd.conf.d/daikin-pi.lircd.conf

# restart LIRC
sudo systemctl restart lircd

# send the command
sudo irsend SEND_ONCE daikin-pi test-signal
```

## Roadmap

Parts of this roadmap may well be built as separate projects.
This is more about my roadmap towards home automation with an old shitty house and appliances.

- [x] Complete state machine flask server
- [x] Write MQTT Adapter for both rx and tx messages to communicate with Home Assistant (
- Build IR rx circuit on Pi
- Bridge IR rx signal decoding to update server state
- Build Temperature & Humidity Sensor
	- Add those sensors to mqtt messaging



### Resources

#### IR/Pi/DaikinProtocol

- https://medium.com/@camilloaddis/smart-air-conditioner-with-raspberry-pi-an-odissey-2a5b438fe984
- http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/
- https://www.raspberrypi.org/forums/viewtopic.php?f=45&t=7798&start=100
- http://www.ivancreations.com/2015/04/control-air-conditioner-with.html
- https://www.hackster.io/gowthamgowda/pi-zero-ir-blaster-amazon-echo-35ae8e
- http://www.lirc.org/api-docs/html/classlirc_1_1client_1_1Command.html#ab9e989920c1f77076b92dee5ff1133af
- https://github.com/opensourcerebel/HomeAutomationServer/tree/master/daikin
- https://github.com/blafois/Daikin-IR-Reverse
- https://blog.bschwind.com/2016/05/29/sending-infrared-commands-from-a-raspberry-pi-without-lirc/
- https://raspberrypi.stackexchange.com/questions/56999/will-this-arduino-module-work-with-raspberry-pi-3
- https://github.com/bschwind/ir-slinger
- https://github.com/joan2937/pigpio/issues/146
- https://raspberrypi.stackexchange.com/questions/74313/pigpio-wave-chaining-count-total-pulses-sent
- https://github.com/blafois/Daikin-IR-Reverse
- https://github.com/arendst/Sonoff-Tasmota/issues/3423
- https://www.raspberrypi.org/forums/viewtopic.php?t=79978

FIX
- https://www.raspberrypi.org/forums/viewtopic.php?t=235918
- https://github.com/AnaviTechnology/anavi-docs/blob/master/anavi-infrared-phat/anavi-infrared-phat.md#setting-up-lirc



#### Home automation

- https://medium.com/@JoooostB/make-your-dumb-old-doorbell-smart-for-just-under-10-using-home-assistant-220cb97ea692


*Merros Lighting with Home Assistant*

- https://github.com/carlosatta/hassio-addons

*bluetooth*

- https://www.cnet.com/how-to/how-to-setup-bluetooth-on-a-raspberry-pi-3/


*Home assistant thermostat sensors*
- https://www.home-assistant.io/components/generic_thermostat/
- https://www.home-assistant.io/components/fan.xiaomi_miio/


*ESP32*
- https://randomnerdtutorials.com/esp32-mqtt-publish-subscribe-arduino-ide/
- https://esphome.io/components/sensor/xiaomi_mijia.html
- https://www.hackster.io/rayburne/esp32-in-love-with-both-cores-8dd948

*MQTT*
- https://diyodemag.com/projects/mqtt_light_switch
