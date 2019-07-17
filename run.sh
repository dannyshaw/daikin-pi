#!/bin/bash

tmux new-session -d -s daikin-pi 'python /home/pi/daikin-pi/daikin/mqtt_service.py'
