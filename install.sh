#!/bin/bash

echo $(date +%F\ %T) Starting installation
echo $(date +%F\ %T) Installing mosquitto MQTT Broker
if [ $(which apt | grep -c apt) -gt 1 ]; then
  echo $(date +%F\ %T) APT detected, using it for installation...
  sudo apt update && sudo apt -y install mosquitto
  RETVAL=$?
else
  if [ $(which dnf | grep -c dnf) -gt 1 ]; then
    echo $(date +%F\ %T) DNF detected, using it for installation...
    sudo dnf -y install mosquitto
    RETVAL=$?
  else
    if [ $(which yum | grep -c yum) -gt 1 ]; then
      echo $(date +%F\ %T) YUM detected, using it for installation...
      sudo dnf -y install mosquitto
      RETVAL=$?
    else
      echo $(date %F\ %T) Unknown package manager, please install Mosquitto or any other MQTT broker manually.
      RETVAL=0
    fi
  fi
fi
if [ $RETVAL -ne 0 ]; then
  echo $(date +%F\ %Y) Installation of mosquitto failed.  Exiting.
  exit $RETVAL
fi
echo $(date +%F\ %T) Copying files...
sudo cp -a usr etc /
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
  echo $(date +%F\ %Y) Copying files failed.  Exiting.
  exit $RETVAL
fi

echo $(date +%F\ %T) Reloading UDEV rules...
sudo udevadm control -R
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
  echo $(date +%F\ %Y) Reloading UDEV rules failed. Auto-start of smpro service may not work.
fi

echo $(date +%F\ %T) Installation complete.  Please now plug in your SMPro.
