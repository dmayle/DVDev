import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from dvdev.lib.base import BaseController, render

from pylons import config
from os import path, makedirs
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

from dvdev.lib import get_sanitized_path
from mercurial import commands, ui, hg

from re import compile

log = logging.getLogger(__name__)


class OpeniduserController(BaseController):

    def login(self):
        return render('login.html')
    def success(self):
        output = ''
        for repo, root in self.repositories:
            #commands.pull(thisui, user_repo)
            self.ui.pushbuffer()
            commands.diff(self.ui, repo)
            output += self.ui.popbuffer()
        css = '<style type="text/css">%s</style>' % HtmlFormatter().get_style_defs('.highlight')
        return self.workspace
        return "%s User: %s" % (css, highlight(output, DiffLexer(), HtmlFormatter()))
