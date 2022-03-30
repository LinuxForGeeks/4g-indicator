4G Indicator
============

A 4G/WiFi indicator for Linux desktops.

![screenshot](screenshot.png)

## Installation

The following dependencies are required:
- python3
- python3-gi
- gir1.2-gtk-3.0
- gir1.2-appindicator3-0.1

To install all the dependencies on debian or derivates, run:
```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

Next, open a terminal in the 4g-indicator folder & run install script:
```bash
sudo ./install.sh
```

To uninstall run:
```bash
sudo ./uninstall.sh
```

## Update

Simply run the install script in `sudo` mode & all files should be updated.

## Credits

Icons made by [Health icons](https://healthicons.org).

## License

4G Indicator is licensed under the [GPL license](LICENSE).
