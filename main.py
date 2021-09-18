__author__ = 'jaap'
"""


"""
# ---
import sys
import os
import os.path as P
import traceback

# ---
import cherrypy as CP
import cherrypy_cors as CC
import mako.template as MT
import mako.lookup

# ---
import settings as S
import api as API
from web import web_support


# ---
class DO(object):
    pass

# ---
class WebServer(object):

    def __init__(self):
        self.template_lookup = self.get_mako_lookup

    def get_mako_lookup(self):
        print([S.PATH_TEMPLATES])
        lookup = mako.lookup.TemplateLookup(directories=[S.PATH_TEMPLATES])
        return lookup

    @CP.expose
    def index(self, **kwargs):
        tmpl_file_name = P.join(S.PATH_TEMPLATES, 'index.tmpl')
        html = MT.Template(filename=tmpl_file_name, lookup=self.template_lookup)
        return html.render()

    @CP.expose
    def users(self):
        tmpl_file_name = P.join(S.PATH_TEMPLATES, 'users.tmpl')
        html = MT.Template(filename=tmpl_file_name, lookup=self.template_lookup)
        data = DO()
        data.users = web_support.get_users()
        return html.render(data=data)

    @CP.expose
    def icons(self):
        index_tmpl = P.join(S.PATH_TEMPLATES, 'icons.tmpl')
        html = MT.Template(filename=tmpl_file_name, lookup=self.template_lookup)
        data = DO()
        data.icons = web_support.get_icons()
        return html.render(data=data)


# ---
def run():
    print("start web server")
    CC.install()
    CP.config.update(S.cp_config)
    CP.tree.mount(WebServer(), '/', S.cp_config)
    config = {'/api': {
             "cors.expose.on": True}}
    CP.tree.mount(API.API(), '/api', config)

    CP.engine.start()
    CP.engine.block()


# ---
if __name__ == "__main__":
    run()
