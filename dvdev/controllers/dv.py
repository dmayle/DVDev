import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from dvdev.lib.base import BaseController, render
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter
from mercurial import commands, ui, hg

log = logging.getLogger(__name__)

class DvController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/dv.mako')
        # or, return a response
        output = ''
        for repo, root in self.repositories:
            #commands.pull(thisui, user_repo)
            self.ui.pushbuffer()
            commands.diff(self.ui, repo)
            output += self.ui.popbuffer()
        c.css = '<style type="text/css">%s</style>' % HtmlFormatter().get_style_defs('.highlight')
        c.diff = highlight(output, DiffLexer(), HtmlFormatter())
        return render('dv/commit.html')

    def commit(self):
        message = request.params['message']
        if not message:
            redirect_to(action='commit')
        for repo, root in self.repositories:
            commands.commit(self.ui, repo, message=message, logfile=None)
        redirect_to(action='index')
