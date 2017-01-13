# AlarmCycleAlignment.py
#
# Resposible for setting the more complex cycle-aligned alarms.
# Also runs its own handler to ensure activation based on the sleep
# now button. 
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

import datetime
from AlarmConstants import *
from AlarmUtility import *

class AlarmCycleAlignment():
    def __init__(self, userInput, config):
        # CONSTANTS
        self.BUTTON_DEBOUNCING_DELAY = 10000 # ms
        self.ACTIVATE_CHIRP_DURATION = 10 # ms
        self.ACTIVATE_CHIRP_SPACING = 250  # ms
        self.DEACTIVATE_BEEP_DUR = 300  # ms
        self.SPEAK_VS_BEEP = True

        # Variables
        self.config = config
        self.lastSetTime = datetime.datetime.min # never set before
        self.userInput = userInput

        # bind alarm-setting handler to the Sleep Now button
        userInput.addSleepNowHandler(self.setAlignedAlarm)

    def getNearestCycleAlignedAlarm(self, desiredWakeup, timeToSleep):
        """ Returns the time [datetime object] of the nearest time (rounds up/down based on DailySetting.MAX_OVERSLEEP)
        that aligns to the 90-minute sleep cycle.
        The desiredWakeup parameter should be a datetime object.
        The timeToSleep parameter should be in minutes. """
        sleepStart = datetime.datetime.today() + datetime.timedelta(seconds=timeToSleep)

        # get number of minutes of sleep (truncate)
        timeToDesiredWakeup = (desiredWakeup - sleepStart).total_seconds() / 60

        if timeToDesiredWakeup < 0:
            log("When trying to set a cycle-aligned alarm, the wakeup time was in the past!")
            return None

        # minutes left over after the next lowest 90-minute sleep cycle
        minutesOffAligned = timeToDesiredWakeup % 90

        # determine time to sleep for (round up if we can hit a sleep cycle while within the user's
        # max oversleep, but round down otherwise)
        sleepTime = 0
        if (90 - minutesOffAligned) < self.config.getDailySetting(getDayFromNum(desiredWakeup.weekday()), DailySetting.MAX_OVERSLEEP) / 60:
            # round up
            sleepTime = timeToDesiredWakeup + (90 - minutesOffAligned)
        else:
            # round down
            sleepTime = timeToDesiredWakeup - minutesOffAligned

        # return a datetime object at the determined time after the to-bed time
        return sleepStart + datetime.timedelta(minutes=sleepTime)

    # this is run as a handler under RPi.GPIO, so needs an extra argument
    def setAlignedAlarm(self, _):
        now = datetime.datetime.today()
        today = getDayFromNum(now.weekday())

        # add more debouncing on top of GPIO; ignore duplicate button presses for a time
        if (now - self.lastSetTime).total_seconds() < self.BUTTON_DEBOUNCING_DELAY / 1000.0:
            return

        todayAlarm = self.config.getTime(today)
        # assume that the person wants to wake up at tommorow's alarm (wrap around on Sunday),
        # UNLESS the current time is before today's alarm (or 8AM if none exists)
        if ((todayAlarm.hour != 0 or todayAlarm.minute != 0) and (now - todayAlarm).total_seconds() < 0) or now.hour < CYCLE_ALIGNED_EARLIEST_SET_TOMMOROW:
            dayOfAlarm = today
        else:
            dayOfAlarm = getDayFromNum((getNumFromDay(today) + 1) % 7)

        # if a cycle-aligned alarm is already set, disable it so the button is a toggle switch
        if self.config.getCycleAlignedTime(dayOfAlarm) != None:
            self.config.setCycleAlignedTime(None, day=dayOfAlarm)
            # re-enable normal alarm... NOTE: THIS IS A BAD WAY TO DO IT; YOU SHOULD CHANGE alarmpi.py SO THAT DISABLING
            # IS NOT NECESSARY (WE JUST SKIP A NORMAL NON-SNOOZE ALARM IF A later CYCLE-ALIGNED IS DEFINED... OR CAN WE??????
            self.config.setState(dayOfAlarm, True)

            if self.SPEAK_VS_BEEP:
                speak("Disabled alarm")
            else:
                self.userInput.alert(self.DEACTIVATE_BEEP_DUR)
        else:
            # get settings (but get them for the day before... this will ensure that even late at night
            # (early in the morning) the logical settings will be used)
            dayBeforeAlarm = getDayFromNum((getNumFromDay(dayOfAlarm) - 1) % 7)
            specificSleepTime = self.config.getDailySetting(dayBeforeAlarm, DailySetting.DESIRED_SLEEP_TIME)
            timeToSleep = self.config.getDailySetting(dayBeforeAlarm, DailySetting.TIME_TO_SLEEP)

            wakeTime = None
            if specificSleepTime != 0:
                wakeTime = now + datetime.timedelta(seconds=timeToSleep + specificSleepTime)
            else:
                desiredWakeup = self.config.getTime(dayOfAlarm)

                wakeTime = self.getNearestCycleAlignedAlarm(desiredWakeup, timeToSleep)

            if (wakeTime):
                # disable normal alarm and set a cycle-aligned one
                self.config.setState(getDayFromNum(wakeTime.weekday()), False)
                self.config.setCycleAlignedTime(wakeTime)

                if self.SPEAK_VS_BEEP:
                    speak("Set at %s. %d hours, %d minutes" % (wakeTime.strftime("%H:%M %p"),
                                                            (wakeTime - now).total_seconds() / 3600,
                                                            ((wakeTime - now).total_seconds() / 60) % 60))
                else:
                    # play a number of beeps corresponding to sleep time
                    for i in range(0, int((wakeTime - now).total_seconds() / 3600)):
                        self.userInput.alert(self.ACTIVATE_CHIRP_DURATION)
                        time.sleep(self.ACTIVATE_CHIRP_SPACING / 1000.0)
            else:
                speak("error")

        self.lastSetTime = now
