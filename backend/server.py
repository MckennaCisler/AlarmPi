#!/usr/bin/python

# server.py
#
# Responsible for specifying parameters of and starting a Tornado
# web server for the configuration web interface of the AlarmPi.
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 1.13.2019

import daemon
import os
import hashlib
import random
import tornado.ioloop
import tornado.web
import tornado.httpserver
from ConfigHandler import *
from AlarmConstants import *
from AlarmConfig import *
import UIModules

# CONSTANTS
LISTEN_PORT = 8888
WEB_ROOT = ROOT_DIRECTORY + "/public"
LOGIN_PASSWORD_HASH = "0127ce4151c7694e87b9e50e71049ebbf39302de88dc6ed72be8e5ae294e9c33"

# Globals (Sorry, they're needed for the MainHandler)
config = AlarmConfig(CONFIG_FILE)

# create base handler to override get_current_user to allow authentication
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return

        self.render("index.html",
                    config=config,
                    days=Days(),
                    dailySettings=DailySettings(),
                    globalSettings=GlobalSettings(),
                    sounds=Sounds(),
                    getFullDayName=getFullDayName,
                    getPrettyName=getPrettyName)

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", message=None)

    def post(self):
        # check password
        password = self.get_argument("password")
        if hashlib.sha256(password).hexdigest() == LOGIN_PASSWORD_HASH:
            self.set_secure_cookie("user", str(random.random()))
            self.redirect("/")
        else:
            self.render("login.html",
                        message="Incorrect password")

def make_app(config):
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/config", ConfigHandler, dict(config=config)),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": WEB_ROOT})
    ],
        static_path=WEB_ROOT,
        template_path=WEB_ROOT,
        ui_modules=UIModules,
        debug=DEBUG,
        cookie_secret = str(os.urandom(24))
    )

def main():
    app = make_app(config)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(LISTEN_PORT)
    log("Starting webserver at localhost:%d" % LISTEN_PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    logFile = open(LOGFILE, "a")
    with daemon.DaemonContext(working_directory=ROOT_DIRECTORY + "/backend", stdout=logFile, stderr=logFile):
        main()
