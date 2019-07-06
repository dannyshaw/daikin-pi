#!/usr/bin/bash

set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE%/*}"

if [ $(id -u) != "0" ]
then
    echo "run as root"
    exit 1
fi

apt install \
  lirc \
  libffi-dev \
  libbz2-dev \
  liblzma-dev \
  libsqlite3-dev \
  libncurses5-dev \
  libgdbm-dev \
  zlib1g-dev \
  libreadline-dev \
  libssl-dev \
  tk-dev \
  build-essential \
  libncursesw5-dev \
  libc6-dev \
  openssl \
  git \
  -y

cp ./hardware.conf /etc/lirc/hardware.conf

echo "lirc_dev" >> /etc/modules
echo "lirc_rpi gpio_in_pin=23 gpio_out_pin=22" >> /etc/modules

cd /opt
wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
tar xf Python-3.6.5.tar.xz
cd Python-3.6.5
./configure --enable-optimizations
make -j -l 4
make altinstall

