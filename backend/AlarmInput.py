# AlarmInput.py
#
# Resposible for interfacing with the physical buttons of the AlarmPi
# via the GPIO. Encapsulaes these button functions and also provides
# simple handler functionality using callbacks.
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

import RPi.GPIO as GPIO
import time

class AlarmInput():
    def __init__(self):
        self.SNOOZE_PIN = 19
        self.DEACTIVATE_PIN = 23
        self.SLEEP_NOW_PIN = 21
        self.ALERT_PIN = 40
        self.ALERT_CYCLE_FREQ = 25 # ms
        self.DEBOUNCE_DELAY = 2000 # ms

        # Setup GPIO
        GPIO.setmode(GPIO.BOARD)

        # pull up all inputs
        GPIO.setup([self.SNOOZE_PIN, self.DEACTIVATE_PIN, self.SLEEP_NOW_PIN], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.ALERT_PIN, GPIO.OUT)

        # Setup initial handlers
        GPIO.add_event_detect(self.SNOOZE_PIN, GPIO.FALLING, callback=self.alert, bouncetime=self.DEBOUNCE_DELAY)
        GPIO.add_event_detect(self.DEACTIVATE_PIN, GPIO.FALLING, callback=self.alert, bouncetime=self.DEBOUNCE_DELAY)

        # notify of startup with beep
        self.alert(0)

    def __del__(self):
        GPIO.remove_event_detect(self.SNOOZE_PIN)
        GPIO.remove_event_detect(self.DEACTIVATE_PIN)
        GPIO.remove_event_detect(self.SLEEP_NOW_PIN)
        GPIO.cleanup()

    def snoozePressed(self):
        return self._pinActive(self.SNOOZE_PIN)

    def deactivatePressed(self):
        return self._pinActive(self.DEACTIVATE_PIN)

    def addSleepNowHandler(self, handler):
        GPIO.add_event_detect(self.SLEEP_NOW_PIN, GPIO.FALLING, callback=self.alert, bouncetime=self.DEBOUNCE_DELAY)
        GPIO.add_event_callback(self.SLEEP_NOW_PIN, handler)

    def _pinActive(self, pin):
        return GPIO.event_detected(pin)

    def clearHandlers(self):
        """ Clears any past button presses by querying all buttons (see self._pinActive)"""
        self.snoozePressed()
        self.deactivatePressed()

    # this is run as a handler under RPi.GPIO, so needs an extra argument
    def alert(self, pin):
        GPIO.output(self.ALERT_PIN, True)
        time.sleep(self.ALERT_CYCLE_FREQ / 1000.0)
        GPIO.output(self.ALERT_PIN, False)

if __name__ == "__main__":
    i = AlarmInput()

