#!/usr/bin/python

# alarmpi.py
#
# A daemon responsible for checking for alarm activations and activating alarms
# at the correct time. Should be run constantly (upon startup) for the alarm to 
# function, but is completely independent of the configuration web interface and 
# associated server.
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

import subprocess as sub
import daemon
import time
import os
import datetime
from AlarmConstants import *
from AlarmConfig import *
from AlarmUtility import *
from AlarmInput import *
from AlarmActivator import *
from AlarmCycleAlignment import *
from AlarmReporting import *


class AlarmPi:
    def __init__(self):
        # CONSTANTS
        self.CHECK_INTERVAL = 30 if DEBUG else 60 # in seconds, <= 60
        self.TIME_TOLERANCE = 2  # distance off time that's considered on time (s)

        # UTILIZED OBJECTS AND VARIABLES
        self.config = AlarmConfig(CONFIG_FILE)
        self.userInput = AlarmInput()
        self.reporting = AlarmReporting(self.userInput)  # start various reporting capabilites

        self.snoozedAlarmTime = None

        self.run()

    def run(self):
        # start listener to automatically setup alarm aligned to user's sleep cycle
        AlarmCycleAlignment(self.userInput, self.config)

        log("Started AlarmPi daemon")

        self.waitForNextCheck()
        while True:
            curDay = self.getCurDay()
            # activate if a normal alarm is active and due, OR if a cycle-aligned alarm is active
            # (the cycle alarm is favored over a normal alarm and only runs once)
            if self.config.getState(curDay) and self.currentlyAtTime(self.config.getTime(curDay)) or \
                    self.currentlyAtTime(self.config.getCycleAlignedTime(curDay)):

                # clear all previous button pushes so they don't interfere, and disable any auxiliary handlers
                self.userInput.clearHandlers()
                self.reporting.disableHandlers()

                # If we have any cycle-aligned alarm set, then re-enable the normal one (for next week).
                # However, if the normal one will go off later, wait until that one activates
                # before deactivating the cycle-aligned alarm, so we can stop that one.
                cycleAlignedTime = self.config.getCycleAlignedTime(curDay)
                if cycleAlignedTime:
                    # if a non-snooze normal alarm is GOING OFF after a cycle-aligned, stop it and reset the cycle-aligned
                    if not self.snoozedAlarmTime and \
                            self.config.getState(curDay) and \
                            self.currentlyAtTime(self.config.getTime(curDay)):

                            self.config.setCycleAlignedTime(None, day=curDay)

                            self.reporting.enableHandlers()  # re-enable auxiliary handlers (briefly)
                            self.waitForNextCheck()
                            continue
                    # if an ACTIVE normal alarm time (or one overwritten by snooze) is after this cycle-alarm, ignore it but don't remove the cycle-aligned
                    # (that normal alarm will be caught above and the cycle-aligned will be deactivated)
                    # Continue with setting off the cycle-aligned alarm
                    elif self.config.getState(curDay) and \
                                    ((self.config.getTime(curDay) if not self.snoozedAlarmTime else self.snoozedAlarmTime)
                                         - cycleAlignedTime).total_seconds() > 0:
                        pass
                    # if the normal one won't go off after, simply deactivate the cycle-aligned
                    # and continue with setting it off
                    else:
                        self.config.setCycleAlignedTime(None, day=curDay)

                alarmStart = datetime.datetime.today()

                alarm = AlarmActivator(self.config, curDay)
                setVolume(self.config.getGlobalSetting(GlobalSetting.ALARM_VOLUME))
                alarm.activate()

                log("Activating alarm on %s at %s; playing %s: '%s'" % (curDay, alarmStart,
                                                                       self.config.getDailySetting(curDay,
                                                                                                   DailySetting.ALARM_TYPE),
                                                                       self.config.getDailySetting(curDay,
                                                                                                   DailySetting.ALARM_SUBTYPE)))

                # break in certain cases
                while True:
                    if self.userInput.deactivatePressed():
                        if self.snoozedAlarmTime != None:
                            self.config.setTime(self.snoozedAlarmTime)  # change alarm back to what it was set to
                            self.snoozedAlarmTime = None

                        log("Alarm deactivated")
                        break

                    elif self.userInput.snoozePressed():
                        self.snoozedAlarmTime = alarmStart

                        # set a new alarm SNOOZE_TIME seconds from now (as set in the config)
                        snoozeLen = datetime.timedelta(seconds=self.config.getGlobalSetting(GlobalSetting.SNOOZE_TIME))

                        # use the day of the final time to avoid bugs near midnight
                        self.config.setTime(alarmStart + snoozeLen)

                        log("Snoozed alarm, will activate again at %s" % (alarmStart + snoozeLen).strftime("%X"))
                        break

                    elif ((datetime.datetime.today() - alarmStart).total_seconds() >=
                              self.config.getGlobalSetting(GlobalSetting.ACTIVATION_TIMEOUT)):
                        log("Alarm timed out")
                        break

                    # slow down processing slightly
                    time.sleep(0.01)

                # deactivate once either a deactivate button is pressed
                # or the alarm times out
                alarm.deactivate()
                self.reporting.enableHandlers() # re-enable auxiliary handlers

            self.waitForNextCheck()

    def currentlyAtTime(self, targetTime):
        if not targetTime: return False

        curTime = datetime.datetime.today()

        if DEBUG: log("Checked the proximity of %s to %s" % (curTime, targetTime))

        return abs(targetTime - curTime).total_seconds() < \
               datetime.timedelta(seconds=self.TIME_TOLERANCE).total_seconds()

    def getCurDay(self):
        dayNum = datetime.datetime.today().weekday()
        return getDayFromNum(dayNum)

    def waitForNextCheck(self):
        curSecs = int(time.strftime("%S"))
        # sleep for the time difference between this time and the nearest whole time
        # of the check interval (relative to the start of this minute)
        time.sleep(self.CHECK_INTERVAL - curSecs % self.CHECK_INTERVAL)


if __name__ == "__main__":
    logFile = open(LOGFILE, "a")
    with daemon.DaemonContext(working_directory=ROOT_DIRECTORY + "/backend", stdout=logFile, stderr=logFile):
        AlarmPi()
