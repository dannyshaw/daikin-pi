#!/bin/bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE%/*}"

if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

apt update
apt install \
  git \
  python-pip \
  vim \
  -y


pip install virtualenv
virtualenv ~/.venvs/daikin

source ~/.venvs/daikin/bin/activate

pip install -r ${SCRIPT_DIR}/requirements.txt

# cp ${SCRIPT_DIR}/hardware.conf /etc/lirc/hardware.conf
# echo "lirc_dev" >> /etc/modules
# echo "lirc_rpi gpio_in_pin=23 gpio_out_pin=22" >> /etc/modules
# echo "dtoverlay=lirc-rpi,gpio_in_pin=23,gpio_out_pin=22" >> /boot/config.txt


echo "--------"
echo "Patching LIRC"
grep '^deb ' /etc/apt/sources.list | sed 's/^deb/deb-src/g' > /etc/apt/sources.list.d/deb-src.list
apt update
apt install \
  devscripts \
  dh-systemd \
  -y

apt build-dep lirc
mkdir ~/build_lirc
cd ~/build_lirc
apt source lirc
wget https://raw.githubusercontent.com/neuralassembly/raspi/master/lirc-gpio-ir.patch
patch -p0 -i lirc-gpio-ir.patch
cd lirc-0.9.4c
debuild -uc -us -b
cd ..
sudo apt install ./liblirc0_0.9.4c-9_armhf.deb ./liblirc-client0_0.9.4c-9_armhf.deb ./lirc_0.9.4c-9_armhf.deb



echo "--------"
echo "Daikin Pi Successfully Installed!"
echo "Ensure settings in daikin-pi/.env are set and reboot"

echo "------------------------------"
