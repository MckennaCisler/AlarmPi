# AlarmReporting.py
#
# Resposible for the functions of the AlarmPi that report information to the user
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 12.31.2016

from AlarmUtility import *
import time, datetime

class AlarmReporting():
    def __init__(self, userInput):
        self.BUTTON_DEBOUNCING_DELAY = 10000 # ms

        self.userInput = userInput
        self.lastSetTime = datetime.datetime.min  # never set before

        self.enableHandlers()

    def disableHandlers(self):
        self.userInput.removeSnoozeHandler()

    def enableHandlers(self):
        self.userInput.addSnoozeHandler(self._timeReportHandler)

    # this is run as a handler under RPi.GPIO, so needs an extra argument
    def _timeReportHandler(self, _):
        now = datetime.datetime.now()

        # add more debouncing on top of GPIO; ignore duplicate button presses for a time
        if (now - self.lastSetTime).total_seconds() >= self.BUTTON_DEBOUNCING_DELAY / 1000.0:
            speak("It is " + time.strftime("%-H:%M"))

        self.lastSetTime = now
