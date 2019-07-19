#!/bin/bash

tmux new-session -d -s daikin-pi '/root/.venvs/daikin/bin/python /home/pi/daikin-pi/daikin/mqtt_service.py'
