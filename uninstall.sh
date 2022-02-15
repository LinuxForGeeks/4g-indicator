#!/bin/bash

if [ "$(id -u)" != "0" ]; then
echo “This script must be run as root” 2>&1
exit 1
fi

rm -rf /usr/share/4gindicator
rm -f /usr/share/applications/4gindicator.desktop
rm -f /etc/xdg/autostart/4gindicator.desktop
rm -f /usr/local/bin/4gindicator
