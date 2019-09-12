#!/bin/bash

#install alfa engine
git clone https://github.com/alfa-addon/addon
mv addon/plugin.video.alfa alfa
rm -Rf addon

#engine installed, now launch patches
cat alfa/core/httptools.py | sed -e "s/HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = config.get_setting('httptools_timeout', default=15)/HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = 15/" > alfa/core/httptools.py.new
mv alfa/core/httptools.py.new alfa/core/httptools.py

#transmission
sudo apt-get install transmission-cli sox python-cryptography ffmpeg -y

#tg for raspberry or debian
#sudo apt-get install libreadline-dev libconfig-dev libssl-dev lua5.2 liblua5.2-dev libevent-dev libjansson-dev libpython-dev libpython3-dev libgcrypt-dev zlib1g-dev lua-lgi make -y
sudo apt-get install libreadline-dev libconfig-dev libssl1.0-dev lua5.2 liblua5.2-dev libevent-dev libjansson-dev libpython-dev libpython3-dev libgcrypt-dev zlib1g-dev lua-lgi make -y
git clone --recursive https://github.com/kenorb-contrib/tg /home/pi/tg
cd /home/pi/tg
./configure
make -j4

echo "done!"
