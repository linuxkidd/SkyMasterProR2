# SkyMaster R2 Python Processor
Python software for processing [Astro-Smart's SkyMaster R2](http://astro-smart.com/index.php?p=1_26_Computerized-Sky-Master-Pro-System-SMP-R2-PRO) USB Serial data


Tested with the no-display version of the SMP-R2-Pro, but should work with SMP-R2-Pro OLED and LCD variants as well.

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

### Automatic Install
This should work for most deb or rpm based distros.

1: Ensure you have sudo access ( or run the following from the root account )
```
git clone https://github.com/linuxkidd/pySkyMasterR2.git
cd pySkyMasterR2
./install.sh
```
2: Investigate / correct any reported errors, or plug in the SMPro.
3: After SMPro is plugged in, the service should start automatically.
4: Check the service is running with:
```
systemctl status smpro@$PORT
```
Where `$PORT` is likely ttyUSB0 -- you can check dmesg output to confirm which port was assigned.


### Manual Install
1. Clone the repo:
```
git clone https://github.com/linuxkidd/pySkyMasterR2.git
```
2. Copy the files to their proper location:
```
cd pySkyMasterR2
sudo cp -a usr etc /
```
3. Reload udev rules:
```
sudo udvadm control -R
```
4. Install Mosquitto ( or other MQTT broker of your choice ):
    - For debian based distros ( including Ubuntu ):
```
apt update && apt -y install mosquitto
```
    - For RPM based distros ( including RHEL, CentOS, Fedora ):
```
dnf -y install mosquitto
```
    - For older RPM based distros:
```
yum -y install mosquitto
```
5. Plug in the SMPro, the service should start automatically.
6. Check the service is running with:
```
systemctl status smpro@$PORT
```
    - Where `$PORT` is likely ttyUSB0 -- you can check dmesg output to confirm which port was assigned.

### NOTE:
- I've observed that the SMPro units sometimes stop responding.
- A restart of the service usually brings it back to life.
```
systemctl restart smpro@$PORT
```
- I'll likely work on an update to catch this condition and respond automatically in the near term.

### Bugs?  Questions?  Comments?
- Please [file an issue](https://github.com/linuxkidd/pySkyMasterR2/issues).

### Want to contribute code?
- Please [submit a pull request](https://github.com/linuxkidd/pySkyMasterR2/pulls).
