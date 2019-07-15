#!/usr/bin/bash

set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE%/*}"

if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

apt install \
  lirc \
  git \
  python-pip \
  -y

pip install virtualenv

virtualenv ~/.venvs/daikin

source ~/.venvs/daikin/bin/activate

pip install -r ${SCRIPT_DIR}/requirements.txt

cp ./hardware.conf /etc/lirc/hardware.conf

echo "lirc_dev" >> /etc/modules
echo "lirc_rpi gpio_in_pin=23 gpio_out_pin=22" >> /etc/modules

reboot
