# AlarmUtility.py
#
# A place for shared utiliy methods, many of which are related to 
# the constants in AlarmConstants.py
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

import time
import subprocess as sub
import urllib, urllib2
import json
from BeautifulSoup import BeautifulSoup
from os import listdir
from os.path import isfile, join
from AlarmConstants import *


def getDayFromNum(dayNum):
    if (dayNum == 0): return Day.MON
    if (dayNum == 1): return Day.TUES
    if (dayNum == 2): return Day.WED
    if (dayNum == 3): return Day.THURS
    if (dayNum == 4): return Day.FRI
    if (dayNum == 5): return Day.SAT
    if (dayNum == 6): return Day.SUN


def getNumFromDay(day):
    if (day == Day.MON):    return 0
    if (day == Day.TUES):    return 1
    if (day == Day.WED):    return 2
    if (day == Day.THURS):    return 3
    if (day == Day.FRI):    return 4
    if (day == Day.SAT):    return 5
    if (day == Day.SUN):    return 6


def getFullDayName(day):
    if (day == Day.MON):    return "Monday"
    if (day == Day.TUES):    return "Tuesday"
    if (day == Day.WED):    return "Wednesday"
    if (day == Day.THURS):    return "Thursday"
    if (day == Day.FRI):    return "Friday"
    if (day == Day.SAT):    return "Saturday"
    if (day == Day.SUN):    return "Sunday"


def getPrettyName(setting):
    setting = setting.replace("_", " ")

    result = ""
    for word in setting.split(" "):
        result += word[0].upper() + word[1:] + " "
    return result[:len(result) - 1]  # remove space


# Functions for returning arrays of constants
def Days():
    dayArr = []
    for day in Day.__dict__.keys():
        if (not day.startswith("__")):
            dayArr.append(Day.__dict__[day])
    # sort return for consistency (in week order with mon at start)
    return sorted(dayArr, key=getNumFromDay)


def DailySettings():
    settingArr = []
    for setting in DailySetting.__dict__.keys():
        if (not setting.startswith("__")):
            settingArr.append(DailySetting.__dict__[setting])
    # sort return for consistency
    return sorted(settingArr)


def GlobalSettings():
    settingArr = []
    for setting in GlobalSetting.__dict__.keys():
        if (not setting.startswith("__")):
            settingArr.append(GlobalSetting.__dict__[setting])
    # sort return for consistency
    return sorted(settingArr)


def Sounds():
    """ Returns all the filenames (sound IDs for this program) of the sounds in the /sounds folder.
	While not techinally returning an array of constants, represents a series of constants. 
	Adapted from http://stackoverflow.com/a/3207973/3155372 """
    return [f[:f.rindex(".")] for f in listdir(SOUNDS_DIRECTORY) if isfile(join(SOUNDS_DIRECTORY, f))]  # Communications


def setVolume(vol):
    """ Sets volume to full where vol==100, so vol is in range(100) """
    sub.call(["amixer", "cset", "numid=1", str(vol) + "%"])

def speak(string):
    log("SPEAKING: " + string)

    setVolume(SPEECH_VOLUME)

    if (YAKITTOME_API_KEY != ""):
        # send request to get audio from YAKItToMe
        # resources:
        # https://www.yakitome.com/documentation/tts_api#markmin_tts
        # https://docs.python.org/2/library/urllib.html#urllib.urlretrieve

        # get the book id, which allows us to get the audio file
        valuesTTS = dict(
            api_key=YAKITTOME_API_KEY,
            voice=YAKITTOME_SPEECH_VOICE,
            speed=YAKITTOME_SPEECH_SPEED,
            text=string)
        jsonTTSResponse = getJSON("http://www.yakitome.com/api/rest/tts", valuesTTS)
        bookID = jsonTTSResponse['book_id']

        # get the url of the relevant audio file
        valuesAudio = dict(
            api_key=YAKITTOME_API_KEY,
            book_id=bookID,
            format="ogg")
        jsonAudioResponse = getJSON("http://www.yakitome.com/api/rest/audio", valuesAudio)
        fileURL = jsonAudioResponse["audios"][0]

        # download file and play it
        location = u"/tmp/" + fileURL[fileURL.rindex("/"):]
        log("Downloading + playing file " + location)
        sub.call(["wget", "--output-document=%s" % location, fileURL])
        sub.call(["play", location, "&"])

    else:
        location = "/tmp/" + str(time.time()) + ".wav"
        sub.call(["pico2wave", "-l=en-US", "-w=%s" % location, string])
        sub.call(["aplay", location])

        """
        # call espeak to get audio data
        espeak_ps = sub.Popen(["espeak", '"' + string + '"',
                               "--stdout",
                               "-s", str(ESPEAK_SPEECH_SPEED),
                               "-v", ESPEAK_SPEECH_VOICE],
                              stdout=sub.PIPE)

        # then pipe it to aplay to fix bitrate issue
        sub.call(["aplay"], stdin=espeak_ps.stdout)
        """


def getJSON(url, values):
    params = urllib.urlencode(values)
    req = urllib2.Request(url, params)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def log(string):
    # add timestamp and newline
    string = "\n" + time.strftime("%c") + ": " + str(string) + "\n"

    with open(LOGFILE, "a") as f:
        f.write(string)

    if DEBUG: print string

if __name__ == "__main__":
    speak("Hello, world")