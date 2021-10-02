__author__ = 'jaap'
"""


"""
# ---
import os.path as P

# ---
import cherrypy as CP
import cherrypy_cors as CC
import mako.template as MT
import mako.lookup

# ---
import settings as S
import api as API
import web_support


# ---
class DO(object):
    pass

# ---
class WebServer(object):

    def __init__(self):
        self.template_lookup = self.get_mako_lookup()

    def get_mako_lookup(self):
        print([S.PATH_TEMPLATES])
        lookup = mako.lookup.TemplateLookup(directories=[S.PATH_TEMPLATES])
        return lookup

    @CP.expose
    def index(self, **kwargs):
        tmpl_file_name = 'index.tmpl'
        html = self.template_lookup.get_template(tmpl_file_name)
        return html.render()

    @CP.expose
    def parties(self):
        tmpl_file_name = 'parties.tmpl'
        html = self.template_lookup.get_template(tmpl_file_name)
        data = DO()
        data.parties = web_support.do(web_support.get_parties)
        return html.render(data=data)

    @CP.expose
    def users(self):
        tmpl_file_name = 'users.tmpl'
        html = self.template_lookup.get_template(tmpl_file_name)
        print("users")
        data = DO()
        data.users = web_support.do(web_support.get_users)
        print(data.users)
        return html.render(data=data)

    @CP.expose
    def logos(self):
        tmpl_file_name = 'logos.tmpl'
        html = self.template_lookup.get_template(tmpl_file_name)
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
