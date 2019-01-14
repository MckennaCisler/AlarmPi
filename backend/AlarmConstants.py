# AlarmConstants.py
#
# A place for storing global constants and "enum"
# classes of constants.
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 1.13.2019

import os

# Global Constants
ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) + "/.." # "/home/pi/sync/Projects/Coding/project/RPi/AlarmPi/"
CONFIG_FILE = ROOT_DIRECTORY + "/alarm-config.json"
LOGFILE = "/tmp/alarmpi-log.log"
SOUNDS_DIRECTORY = ROOT_DIRECTORY + "/sounds/"
PIANOBAR_FIFO = "/home/pi/.config/pianobar/ctl"
PIANOBAR_STATE_FILE = "/home/pi/.config/pianobar/state"
AUTO_SET_AUDIO_DEVICE = True
SPEECH_VOLUME = 80 # percent
ESPEAK_SPEECH_VOICE = "en+m3"  # en+f4 # see http://espeak.sourceforge.net/languages.html
ESPEAK_SPEECH_SPEED = 150
YAKITTOME_SPEECH_VOICE = "Audrey" # see https://www.yakitome.com/documentation/tts_voices
YAKITTOME_SPEECH_SPEED = 5
YAKITTOME_API_KEY = "" #"utvWYeYhzFJtl1ausX690QY"
DEBUG = True

SOUND_FILE_EXT = ".wav"
REPEAT_NUM = 50 # number of times to loop sounds
CYCLE_ALIGNED_EARLIEST_SET_TOMMOROW = 8 # hour (24hr) of the day to switch to setting cycle-aligned alarm for the next day


# Constant "Enum" Classes
class Day:
    MON = "mon"
    TUES = "tues"
    WED = "wed"
    THURS = "thurs"
    FRI = "fri"
    SAT = "sat"
    SUN = "sun"

class AlarmType:
    SOUND = "sound"
    PANDORA = "pandora"

# NOTES:
# All daily settings are designed to be set and changed globally as well (via iteration)
# All duration values are in seconds
# See AlarmConfig._generateNewConfig() for default values (they're only used there)

class DailySetting:
    ALARM_TYPE = "type"
    ALARM_SUBTYPE = "subtype"
    TIME_TO_SLEEP = "time_to_sleep"  # seconds
    DESIRED_SLEEP_TIME = "desired_sleep_time"  # seconds; desired time to sleep for using cycle-aligned alarm
    MAX_OVERSLEEP = "max_oversleep"     # seconds; max time for a cycle-aligned alarm to go over the desired wakeup
                                        # (O means always round down; 90 (maximum) means always round up)

class GlobalSetting:
    ALARM_VOLUME = "alarm_volume"  # value is in range(100)
    SNOOZE_TIME = "snooze_time"  # value is time in seconds to snooze for
    ACTIVATION_TIMEOUT = "activation_timeout"  # value is time in seconds to wait before forcing alarm shutdown
    PANDORA_EMAIL = "pandora_email"  # pandora username and password
    PANDORA_PASS = "pandora_pass"
