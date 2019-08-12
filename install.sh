#!/bin/bash

#install alfa engine
git clone https://github.com/alfa-addon/addon
mv addon/plugin.video.alfa alfa
rm -Rf addon

#engine installed, now launch patches
cat alfa/core/httptools.py | sed -e "s/HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = config.get_setting('httptools_timeout', default=15)/HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = 15/" > alfa/core/httptools.py.new
mv alfa/core/httptools.py.new alfa/core/httptools.py
