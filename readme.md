# Raspberry Pi IR Gateway for Daikin ARC remote control

I wanted to be able to control my old Daikin split system from the internet. Specifically to be able to switch it on from the bedroom on a cold morning or on the way home if we're out of the house. This functionality comes with newer systems and there are 3rd party units available to do this but I was up for the challenge of implementing it myself.

I went about building an IR transmitter gateway to send signals to the unit as though someone were pressing the remote.
This could not have been done without standing on the shoulders of giants before me, specfically those who used an osciloscope and did the actual hard work of reverse engineering the IR Protocol.

Split system AC's like Daikin have complex IR protocols. They do not send single button codes like a TV would receive (VOL_UP) etc. The full state of the air condioner is actually stored _on_ the remote control (so you can see the state on it). Because of this each transmission actually contains the entire state of the system in a long message. (Cool Mode, 19 Degrees, Vertical Swing On, etc).

This means we cannot just have a pool of codes to send, (welll, you could store every single permutation of every setting i guess). But instead build up the state we'd like to set the AC to and generate the message of codes that need to be transmitted to the unit.

### How it works

There is a standard linux program to transmit and receive IR signals called [LIRC](http://www.lirc.org/).
It uses configuration files to define a "remote" from which you can send key code signals
This program builds a single message and writes a configuration file to represent that message and restarts the LIRC daemon
It then executes an LIRC command to send that message.

Additionally there are modules for web and MQTT interfaces.


This repository contains python modules to:
   - Represent the Daikin state
   - Represent that state as a binary message that the Daikin unit can receive
   - Convert binary messages into an LIRC remote configuration (using IR pulse and gap lengths that the unit can receive)
   - A persistance module to store the AC state in a JSON file
   - A webserver to modify the state and transmit it
   - An MQTT Client to react to MQTT Messages and control the state

Tested on my split system which uses a remote with the model number `ARC433B70`

## Installation

### The Circuit

Build this circuit(you can skip the receiver if you want) and use gpio pins 22 and 23 for out and in respectively
https://upverter.com/design/alexbain/f24516375cfae8b9/open-source-universal-remote/#/



### Install Raspbian Stretch

Install a fresh copy of Rasbian Stretch Lite (for Zero, you could use non lite for 3b+ or 4).

NOTE: **It's important to have the linux kernel pinned to 4.14**

So either don't run `apt upgrade` after install or ensure the kernel remains at 4.14 (see below)

My current understanding (work in progress):
Since Rasbian Buster (4.19) came out the modules for IR control changed from `lirc_rpi` to `gpio_ir_recv` and `gpio_ir_tx` (or something, check). However, the latest LIRC has not been upgraded to reflect these changes as yet. There are some patches floating around but pinning to 4.14 is the way I chose.

If you do run `apt upgrade` and would like to roll back to 4.14 do this:
```
sudo apt install rpi-update
sudo rpi-update a08ece3d48c3c40bf1b501772af9933249c11c5b  # last commit on 4.19
```

### Installation Script

Install git and clone this repo to `/home/pi/daikin-pi`.
There's an installation script located in `install/install.sh` run this command to install all prerequisites and configure LIRC. Reboot.

From there you can run the MQTT server by running

`sudo /root/.venvs/daikin/bin/python /home/pi/daikin-pi/daikin/mqtt_server.py`


There's also a statup script called `run.sh` which will auto run the mqtt service within a tmux session on boot
This allows you to just plug it in and it'll connect to the server

Add this line to `/etc/rc.local` to install it:

`/home/pi/daikin-pi/run.sh`

You can then see the running command after booting by entering `sudo tmux attach`


### Alternatively, Configure LIRC Manually

Assumes the use of gpio pin 22 for tx, 23 for rx, edit accordingly.

Install LIRC
```
$ sudo apt install lirc
```

Ensure this line in /boot/config.txt:
```
dtoverlay=lirc-rpi,gpio_in_pin=23,gpio_out_pin=22,gpio_in_pull=up
```

Add these lines to /etc/modules
```
lirc_dev
lirc_rpi gpio_in_pin=23 gpio_out_pin=22
```

Reboot

## Test LIRC Circuit with a simple IR signal to test it works

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

### Configure Systemd to remove rate limit on restarting lircd service

For some reason systemd by default restricts how often you can restart a service and we need to have no such restriction.

`sudo vim /lib/systemd/system/lircd.service`

Add the two lines below

```
[Service]
...
StartLimitIntervalSec=0
StartLimitBurst=0
```


###

Run the MQTT Service


## Home Assistant

The MQTT Client was built to be used with Home Assistant.
The [MQTT HVAC component](https://www.home-assistant.io/components/climate.mqtt/) can be configured to talk to the unit, this configuration is how mine is set up but you can adjust the :

```
# configuration.yaml

climate:
  - platform: mqtt
    name: "Living Room"
    initial: 20
    modes:
      - "off"
      - "auto"
      - "cool"
      - "heat"
      - "fan_only"
    swing_modes:
      - "both"
      - "vertical"
      - "horizonal"
      - "off"
    fan_modes:
      - "high"
      - "medium"
      - "low"
      - "auto"
    power_command_topic: "livingroom/ac/power/set"
    mode_command_topic: "livingroom/ac/mode/set"
    temperature_command_topic: "livingroom/ac/temperature/set"
    fan_mode_command_topic: "livingroom/ac/fan/set"
    swing_mode_command_topic: "livingroom/ac/swing/set"
    max_temp: 30
    min_temp: 18
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



### Resources (For this project and a load of other crap i'm interested in)


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

New Circuit for Receiver and more powerful TX:
https://upverter.com/design/alexbain/f24516375cfae8b9/open-source-universal-remote/#/


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
