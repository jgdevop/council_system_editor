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
import mako
import mako.lookup

# ---
class API(object):
    @CP.expose
    def index(self, **kwargs):
        index_tmpl = P.join(S.PATH_TEMPLATES, 'index.tmpl')
        html = mako.lookup.get_template(filename=index_tmpl, lookup=self.get_mako_lookup())
        return html.render()
