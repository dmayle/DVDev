import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from dvdev.lib.base import BaseController, render

# This is the mercurial WSGI web server
from mercurial.hgweb.hgwebdir_mod import hgwebdir
from pylons import config
from os import path

# We build a list of repositorie tuples consisting of the project name, and their directory
repositories = [(path.basename(repo), repo) for repo in config.get('repo').split()]

log = logging.getLogger(__name__)

class MercurialgatewayController(BaseController):

    def __call__(self, environ, start_response):
        application = hgwebdir(repositories)
        return application(environ, start_response)

