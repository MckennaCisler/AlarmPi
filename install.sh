#!/bin/sh

# Installation for AlarmPi
# Installs requirements and sets up pianobar
# Mckenna Cisler
# 6.11.2016

if [ $(id -u) -ne 0 ]; then
	echo "This script must be run as root"
	exit 1
fi

# get updates
sudo apt-get -y update

if [ $? -ne 0 ]; then
 echo "Could not update repositories"
 exit 1; 
fi

# install dependencies
while read line; do
	sudo apt-get -y install $line
done <requirements.txt

# setup fifo for controlling pianobar
mkdir -p ~/.config/pianobar 
mkfifo ~/.config/pianobar/ctl

if [ $? -ne 0 ]; then
 echo "Could not create fifo for pianobar"
 exit 1; 
fi

# add startup file
mkdir -p ~/.config/upstart/
printf 'description "AlarmPi alarm clock and configuration server" \nauthor "Mckenna Cisler" \nstart on runlevel [2456] \nstop on shutdown \nscript \nexec python /home/pi/sync/Projects/Coding/RPi/AlarmPi/backend/alarmpi.py \npython /home/pi/sync/Projects/Coding/RPi/AlarmPi/backend/server.py \nend script\n' > ~/.config/upstart/alarmpi.conf

echo "*****Reboot to complete changes*****"

#xdg-open http://everyday-tech.com/how-to-install-pianobar-on-the-raspberry-pi/
