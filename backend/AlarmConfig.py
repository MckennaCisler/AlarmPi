# AlarmConfig.py
#
# Resposible for interfacing with the configuration file storing
# alarm settings. Encapsulates file reads and writes as setting
# getting and setting.
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

import datetime
import json
from AlarmConstants import *
from AlarmUtility import *


class AlarmConfig():
    def __init__(self, filename):
        # CONSTANTS
        self.BACKUP_FILE_SUFFIX = "~"

        self.filename = filename
        self._fileCache = {}

        # make sure we have a valid cached config, and backup file in case
        self._cacheConfig()
        self._backupConfig()

    def getState(self, day):
        self._cacheConfig()
        return self._fileCache[day]["state"]

    def setState(self, day, state):
        self._fileCache[day]["state"] = state
        self._updateConfig()

    def getIgnoreState(self, day):
        self._cacheConfig()
        return self._fileCache[day]["ignore-state"]

    def setIgnoreState(self, day, state):
        self._fileCache[day]["ignore-state"] = state
        self._updateConfig()

    def getTime(self, day):
        self._cacheConfig()
        # we use the current time to ensure that any timedeltas
        # taken are of resonable size, but we shift the day around
        # (forwards; we assume we only want to know about future alarms)
        # to make sure the datetime has the same day as requested
        today = datetime.datetime.today()

        basicTime = datetime.datetime(today.year,
                                      today.month,
                                      today.day,
                                      hour=self._fileCache[day]["time-hr"],
                                      minute=self._fileCache[day]["time-min"])

        # shift the basicTime up the number of days required to match the given day
        daysOffFromCorrectDay = datetime.timedelta(days=(getNumFromDay(day) - today.weekday()) % 7)
        return basicTime + daysOffFromCorrectDay

    def setTime(self, timeObj, day=None):
        """ Sets time in config, using day as specified in the passed datetime object,
            UNLESS the day is provided explicitly by the argument. """

        # override day if it's None
        if not day:
            day = getDayFromNum(timeObj.weekday())

        self._fileCache[day]["time-hr"] = timeObj.hour
        self._fileCache[day]["time-min"] = timeObj.minute
        self._updateConfig()

    # The following store/receive a cycle-aligned wakeup time (will be favored over a normal time and only runs once)

    def getCycleAlignedTime(self, day):
        self._cacheConfig()

        hr = self._fileCache[day]["aligned-time-hr"]
        min = self._fileCache[day]["aligned-time-min"]

        # handle non-active alarm
        if hr < 0 or min < 0: return None

        # we use the current time to ensure that any timedeltas
        # taken are of reasonable size (we assume the time returned here
        # is used soon after this is called)
        today = datetime.datetime.today()
        return datetime.datetime(today.year,
                                 today.month,
                                 today.day,
                                 hour=hr,
                                 minute=min)

    def setCycleAlignedTime(self, timeObj, day=None):
        """ Sets time in config, using day as specified in the passed datetime object """

        # disable cycle-aligned if null timeObj given
        if timeObj:
            # override day if it's None (using the time from the timeObj)
            if not day:
                day = getDayFromNum(timeObj.weekday())

            self._fileCache[day]["aligned-time-hr"] = timeObj.hour
            self._fileCache[day]["aligned-time-min"] = timeObj.minute
        else:
            # override day if it's None (using the current day's day
            if not day:
                day = getDayFromNum(datetime.datetime.today().weekday())

            self._fileCache[day]["aligned-time-hr"] = -1
            self._fileCache[day]["aligned-time-min"] = -1

        self._updateConfig()

    def getDailySetting(self, day, setting):
        self._cacheConfig()
        return self._fileCache[day][setting]

    def setDailySetting(self, day, setting, value):
        # make sure it is stored as an appropriate type in any case
        if (value.isnumeric()):
            value = int(value)

        self._fileCache[day][setting] = value
        self._updateConfig()

    def getGlobalSetting(self, setting):
        """ Returns the value of global settings as specified under AlarmConstants.GlobalSetting,
        but also the value of any AlarmConstant.DailySetting that has a common value across days. """
        self._cacheConfig()
        settingVal = None
        try:
            settingVal = self._fileCache[setting]
        except KeyError:
            # if no global setting exists, try finding the value as a daily setting
            # (if all days are the same it'll be a global, but otherwise we'll just give today's setting)
            settingVal = self.getDailySetting(getDayFromNum(datetime.datetime.today().weekday()), setting)

        return settingVal

    def setGlobalSetting(self, setting, value):
        # make sure it is stored as an appropriate type in any case
        if (value.isnumeric()):
            value = int(value)

        self._fileCache[setting] = value
        self._updateConfig()

    def _generateNewConfig(self):
        jsonText = "{"

        for setting in GlobalSettings():
            # set particular defaults for particular settings
            default = '""'
            if setting == GlobalSetting.ACTIVATION_TIMEOUT: default = 15 * 60 # seconds
            elif setting == GlobalSetting.ALARM_VOLUME: default = 100
            elif setting == GlobalSetting.SNOOZE_TIME: default = 10 * 60 # seconds

            jsonText += '"%s":%s,' % (setting, default)

        for day in Days():
            jsonText += '"%s":' % day
            jsonText += '{"state":false, "time-hr":0, "time-min":0, "aligned-time-hr":-1, "aligned-time-min":-1'

            # add any additional daily settings
            for setting in DailySettings():
                # set particular defaults for particular settings
                default = '""'
                if setting == DailySetting.MAX_OVERSLEEP: default = 15 * 60  # seconds
                elif setting == DailySetting.TIME_TO_SLEEP: default = 14 * 60   # seconds; average human time
                                                                                # according to http://sleepyti.me
                elif setting == DailySetting.DESIRED_SLEEP_TIME: default = 0
                elif setting == DailySetting.ALARM_TYPE: default = '"' + AlarmType.SOUND + '"'

                jsonText += ', "%s":%s' % (setting, default)

            jsonText += '},'

        # remove trailing comma before final brace
        jsonText = jsonText[:len(jsonText) - 1] + "}"

        with open(self.filename, "w") as outputF:
            outputF.write(jsonText)

        self._fileCache = json.loads(jsonText)

    def _cacheConfig(self):
        try:
            with open(self.filename, "r") as inputF:
                self._fileCache = json.loads(inputF.read())
        except IOError:
            log("Configuration file not found, generating a new one.")
            self._generateNewConfig()

    def _updateConfig(self):
        with open(self.filename, "w") as outputF:
            outputF.write(json.dumps(self._fileCache, sort_keys=True,
                                     indent=4, separators=(',', ': ')))

    def _backupConfig(self):
        with open(self.filename, "r") as inputF:
            with open(self.filename + self.BACKUP_FILE_SUFFIX, "w") as outputF:
                outputF.write(inputF.read())


if __name__ == "__main__":
    test = AlarmConfig("../default.json")
    test._updateConfig()
