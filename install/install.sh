#!/bin/bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE%/*}"

if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

apt update
apt install \
  tmux \
  lirc \
  vim \
  -y

wget -O - https://bootstrap.pypa.io/get-pip.py | python
pip install virtualenv
virtualenv ~/.venvs/daikin

source ~/.venvs/daikin/bin/activate

pip install -r ${SCRIPT_DIR}/requirements.txt

# create json state file for daikin pi
if [ ! -f "${SCRIPT_DIR}/../data/config.json" ]; then
  mkdir -p ${SCRIPT_DIR}/../data
  echo "{}" > ${SCRIPT_DIR}/../data/config.json
fi


echo "-- Configuring LIRC"
if grep -q "lirc_dev" /etc/modules;
  then
    echo "lirc_dev" >> /etc/modules
fi
if grep -q "^lirc_rpi" /etc/modules;
  then
    echo "lirc_rpi gpio_in_pin=23 gpio_out_pin=22" >> /etc/modules
fi

if grep -q "^dtoverlay=lirc-rpi" /boot/config.txt;
  then
    echo "dtoverlay=lirc-rpi,gpio_in_pin=23,gpio_out_pin=22" >> /boot/config.txt
fi

echo "--------"
echo "Daikin Pi Successfully Installed!"
echo "Reboot and test LIRC"
echo "------------------------------"
