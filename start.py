#!/usr/bin/python
import os
import time

time.sleep(20)
os.system('sudo -u pi python /home/pi/AlarmPi/backend/server.py')
os.system('sudo -u pi python /home/pi/AlarmPi/backend/alarmpi.py')
