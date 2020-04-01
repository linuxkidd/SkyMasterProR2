# SkyMaster R2 Python Processor
Python software for processing Astro-Smart's SkyMaster R2 USB Serial data

Tested with SMP-R2, but should work with SMP-R2-Pro and SMP-R2-Pro OLED.

Can display data direct to console, but intended for normal use bridging data to an MQTT broker.

```
$ ./smpro.py  --help
usage: smpro.py [-h] [-p PORT] [-d {0,1,2}] [-m {0,1,2}] [-b BROKER]
                [-s {0,1}]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  commuications port descriptor, e.g /dev/ttyUSB0 or
                        COM1
  -d {0,1,2}, --debug {0,1,2}
                        debug data
  -m {0,1,2}, --mqtt {0,1,2}
                        Send to MQTT, 1=Publish, 2=Retain
  -b BROKER, --broker BROKER
                        Hostname or IP of MQTT Broker to which to publish.
  -s {0,1}, --stdout {0,1}
                        Print on StdOut
```

Copy the included `99-smpro_usb.rules` to `/etc/udev/rules.d/' then run `udevadm control -R`.  This way, a symlink of /dev/ttySMPRO will be created for use with the script so that it work no matter the USB enumeration order.
