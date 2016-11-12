# UIModules.py
#
# A place for shared Tornado UIModule classes.
#
# Mckenna Cisler
# mckennacisler@gmail.com
# 7.4.2016

import tornado.web
import tornado.template


class AdvancedDropdown(tornado.web.UIModule):
    def render(self, config, sounds, day=None):
        return self.render_string("advanced_dropdown.html", config=config, sounds=sounds, day=day)


class TypeSelect(tornado.web.UIModule):
    def render(self, config, sounds, day=None):
        return self.render_string("type_select.html", config=config, sounds=sounds, day=day)
