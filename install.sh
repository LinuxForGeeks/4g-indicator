#!/bin/bash

if [ "$(id -u)" != "0" ]; then
echo “This script must be run as root” 2>&1
exit 1
fi

sh uninstall.sh

mkdir /usr/share/4gindicator
cp -R resources /usr/share/4gindicator/

cp *.py /usr/share/4gindicator/
chmod 755 -R /usr/share/4gindicator/

cp 4gindicator.desktop /etc/xdg/autostart/
chmod 755 /etc/xdg/autostart/4gindicator.desktop

cp 4gindicator.desktop /usr/share/applications/
chmod 755 /usr/share/applications/4gindicator.desktop

ln -s /usr/share/4gindicator/4gindicator.py /usr/local/bin/4gindicator
chmod 755 /usr/local/bin/4gindicator
