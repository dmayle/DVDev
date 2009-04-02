import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from dvdev.lib.base import BaseController, render
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter
from mercurial import commands, ui, hg, patch, cmdutil
from re import compile
from filesafe import Chroot

# Regex to pull the filename out of the diff header
DIFF_FILE = compile(r'diff -r [0-91-f]+ (.*)$')

log = logging.getLogger(__name__)

class DvController(BaseController):

    def index(self):
        """Go through all of the repositories and list any uncommitted changes"""
        diffs = []
        for repo, root in self.repositories:
            #commands.pull(thisui, user_repo)

            # The hg diff command returns the entire set of diffs as one big
            # chunk.  The following code is lifted from the source (version
            # 1.2) as the method for getting the individual diffs.  As such,
            # this is prone to break in the case of internal changes.  We
            # should try and get an external method to do the same thing.
            node1, node2 = cmdutil.revpair(repo, None)

            match = cmdutil.match(repo, (), {})
            for diff in patch.diff(repo, node1, node2, match=match, opts=patch.diffopts(self.ui)):
                diffheader = diff.split('\n')[0]
                filename = DIFF_FILE.match(diffheader).groups()[0]
                # Should I instantiate a single lexer and formatter and share them?
                diffs.append({'repository':root,
                               'filename':filename,
                               'diff': highlight(diff, DiffLexer(), HtmlFormatter())})
            
        c.css = '<style type="text/css">%s</style>' % HtmlFormatter().get_style_defs('.highlight')
        c.diffs = diffs
        return render('dv/commit.html')

    def commit(self):
        """Use the list of files given by the user to commit to the repository"""
        # The variable passing schema we use means that we'll have problems
        # with a repository named 'on'.  We should look into a fix for that.
        url = request.environ['routes.url']
        io = request.params
        changeset = {}
        for key in request.params:
            input = request.params.getall(key)
            if len(input) != 2:
                continue
            if 'on' not in input or u'on' not in input:
                continue
            if input[1] == 'on' or input[1] == u'on':
                input.pop()
            repo = input.pop()
            changeset[repo] = changeset.get(repo, {})
            changeset[repo][key] = True

        message = request.params['message']
        if not message:
            redirect(url.current(action='index'))
        for repo, root in self.repositories:
            if root not in changeset:
                continue
            repochroot = Chroot(repo.root)
            try:
                files = (repochroot('./' + file) for file in changeset[root])
            except IOError:
                error = 'Bad Filename'
                redirect(url.current(action='index', error=error))
            commands.commit(self.ui, repo, message=message, logfile=None, *files)
        redirect(url.current(action='index'))
