# ConfigHandler.py
#
# A Tornado RequestHandler providing am external POST interface
# for setting values in the alarm configuration file. 
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

from AlarmConstants import *
from AlarmConfig import *
from AlarmUtility import *
import server

import tornado
from tornado.web import HTTPError


class ConfigHandler(server.BaseHandler):
    def initialize(self, config):
        self.config = config

    def post(self):
        """ Handles query-argument post requests for altering alarm settings.
        The query syntax is as follows:

        A request specifying a day must also contain specifications for either
        the alarm state, time, subType, type AND subType, or any other daily
        setting defined in AlarmConstants.py:
            day=[mon|tues|wed|thurs|fri|sat|sun]
            state=[on|off]
            time=HH:MM
            type=[sound|pandora]
            subtype=[<sound in /sounds/>|<pandora station under specified account>]
            <daily setting>=<setting value>

        A request can also set any of the global OR daily settings defined in AlarmConstants.py:
            <global setting>=<setting value>
            <daily setting>=<setting value>

        """
        # ensure user is authenticated
        if not self.current_user:
            self.logError("User must authenticate before changing configuration")
            self.redirect("/login")
            return

        # try to set all possible global settings
        for settingName in GlobalSettings():
            settingValue = self.get_body_argument(settingName, default=False)

            # set any setting included in the post
            if (settingValue):
                self.config.setGlobalSetting(settingName, settingValue)
                log("Set global setting '%s' to value '%s'" % (settingName, settingValue))

                # exception, set volume immediately.
                if (settingName == GlobalSetting.ALARM_VOLUME):
                    setVolume(settingValue)

        # try to set settings for an alarm on a particular day
        day = self.get_body_argument("day", default=False)
        if (day):
            if (day in Days()):
                # try to get all daily settings (do some specifically for more checking later
                state = self.get_body_argument("state", default=False)
                disableAligned = self.get_body_argument("disable_aligned", default=False)
                timeStr = self.get_body_argument("time", default=False)
                alarmType = self.get_body_argument(DailySetting.ALARM_TYPE, default=False)
                subType = self.get_body_argument(DailySetting.ALARM_SUBTYPE, default=False)
                
                print disableAligned
                
                otherSettings = {}
                for settingName in DailySettings():
                    # ignore alarm type and subtype because we got them
                    if (not settingName == DailySetting.ALARM_TYPE
                        and not settingName == DailySetting.ALARM_SUBTYPE):
                        settingValue = self.get_body_argument(settingName, default=False)

                        # only add specified settings
                        if (settingValue):
                            otherSettings[settingName] = settingValue

                # ensure it was a correctly-formed request
                if (state or disableAligned or timeStr or subType or alarmType or len(otherSettings.keys()) > 0):
                    # cumulatively (without newlines) log all changes
                    logStr = "Set (on %s) " % day

                    if (state):
                        self.config.setState(day, state == "on")
                        logStr += "alarm state to '%s', " % ("on" if state == "on" else "off")
                    
                    if (disableAligned):
                        self.config.setCycleAlignedTime(None, day)
                        logStr += "cycle aligned alarm disabled, "

                    if (alarmType and alarmType in AlarmType.__dict__.values()):
                        self.config.setDailySetting(day, DailySetting.ALARM_TYPE, alarmType)
                        logStr += "alarm type to '%s', " % alarmType
                    else:
                        # only warn if not empty
                        if (alarmType):
                            self.logError("Invalid alarm type specified in request to ConfigHandler (/config)")

                    if (subType):
                        self.config.setDailySetting(day, DailySetting.ALARM_SUBTYPE, subType)
                        logStr += "alarm subtype to '%s', " % subType

                    # parse time as well (expected to resemble the partial-time in https://www.w3.org/TR/html-markup/references.html#refsRFC3339)
                    if (timeStr):
                        try:
                            firstColon = timeStr.index(":")
                            lastColon = timeStr.rindex(":", firstColon)
                            today = datetime.datetime.today()
                            time = datetime.datetime(today.year,
                                                     today.month,
                                                     today.day,
                                                     hour=int(timeStr[:firstColon]),
                                                     minute=int(timeStr[firstColon + 1: len(timeStr) if firstColon == lastColon else lastColon]))

                            self.config.setTime(time, day)
                            logStr += "alarm time to %s, " % timeStr
                        except ValueError as e:
                            self.logError("Invalid time specified in request to ConfigHandler (/config): %s" % e)

                    # set any other settings
                    for settingName, settingValue in otherSettings.items():
                        self.config.setDailySetting(day, settingName, settingValue)
                        logStr += "setting '%s' to value '%s', " % (settingName, settingValue)

                    log(logStr)
                else:
                    self.logError("Malformed alarm set request sent to ConfigHandler (/config)")
            else:
                self.logError("Invalid day specified in request to ConfigHandler (/config)")
        else:
            # try to set all possible daily settings for every day ONLY IF
            # a specific day is not being set
            for settingName in DailySettings():
                settingValue = self.get_body_argument(settingName, default=False)

                # set any setting included in the post
                if (settingValue):
                    for day in Days():
                        self.config.setDailySetting(day, settingName, settingValue)

                    log("Set daily setting '%s' to value '%s'" % (settingName, settingValue))

                    # exception, set volume immediately.
                    if (settingName == GlobalSetting.ALARM_VOLUME):
                        setVolume(settingValue)

    def get(self):
        # just send the JSON of the config file (if we can)
        try:
            with open(CONFIG_FILE, "r") as configF:
                self.write(configF.read())
        except IOError, ValueError:
            raise HTTPError(500, "Could not open configuration file at " + CONFIG_FILE)

    def logError(self, error):
        log(error)
        raise HTTPError(400, error)
