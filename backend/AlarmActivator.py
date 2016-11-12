# AlarmActivator.py
#
# Resposible for activating and managing
# the sound aspects of the alarm when it is going off.
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

import subprocess as sub
import os
import os.path
from AlarmConstants import *
from AlarmConfig import *


class AlarmActivator():
    def __init__(self, config, day):
        self.alarmType = config.getDailySetting(day, DailySetting.ALARM_TYPE)
        self.subType = config.getDailySetting(day, DailySetting.ALARM_SUBTYPE)
        self.pandoraEmail = config.getGlobalSetting(GlobalSetting.PANDORA_EMAIL)
        self.pandoraPass = config.getGlobalSetting(GlobalSetting.PANDORA_PASS)
        self._soundProcess = None

        # ensure set on headphone jack
        sub.call(["amixer", "cset", "numid=3", "1"])

    def activate(self):
        if (self._soundProcess != None):
            self._soundProcess.kill()

        if (self.alarmType == AlarmType.SOUND):
            self._activateSound(self.subType)
        elif (self.alarmType == AlarmType.PANDORA):
            self._activatePandora(self.subType)

    def _activateSound(self, sound):
        self._soundProcess = sub.Popen(["play", SOUNDS_DIRECTORY + sound + SOUND_FILE_EXT, "repeat", str(REPEAT_NUM)],
                                       stdout=(None if DEBUG else sub.PIPE))

    # TODO: Check if successful

    def _activatePandora(self, station):
        # make sure that pianobar's automatic station selection is not set (it's set in this file)
        if (os.path.isfile(PIANOBAR_STATE_FILE)):
            os.remove(PIANOBAR_STATE_FILE)

        # start pianobar (ignore stdout by piping)
        self._soundProcess = sub.Popen(["pianobar"], stdout=(None if DEBUG else sub.PIPE))

        # open FIFO to send data to pianobar - see http://linux.die.net/man/1/pianobar under "Remote Control"
        with open(PIANOBAR_FIFO, "w") as fifoInput:
            fifoInput.write(self.pandoraEmail + "\n")
            fifoInput.write(self.pandoraPass + "\n")
            fifoInput.write(station + "\n")
        # TODO: Check if successful

    def deactivate(self):
        if (self._soundProcess != None):
            self._soundProcess.kill()


if __name__ == "__main__":
    import time

    test = AlarmActivator(AlarmConfig('../alarm-config.json'),'thurs')
    print test.subType
    test.activate()
    time.sleep(5)
    test.deactivate()
