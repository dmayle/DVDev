import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from dvdev.lib.base import BaseController, render
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter
from mercurial import commands, ui, hg, patch, cmdutil
from re import compile
from os import path
from filesafe import Chroot
import yamltrak

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
            repodiffs = []
            for diff in patch.diff(repo, node1, node2, match=match, opts=patch.diffopts(self.ui)):
                diffheader = diff.split('\n')[0]
                filename = DIFF_FILE.match(diffheader).groups()[0]
                # Should I instantiate a single lexer and formatter and share them?
                repodiffs.append({'repository':root,
                               'filename':filename,
                               'diff': highlight(diff, DiffLexer(), HtmlFormatter())})
            # At the repo level, we want to go through all found files and look
            # for related issues
            try:
                issues = yamltrak.issues([repo.root])[root]
            except IndexError:
                # There is no issue database, or maybe just no open issues...
                issues = {}
            for diff in repodiffs:
                relatedissues = yamltrak.relatedissues(repo.root, filename=diff['filename'], ids=issues.keys())
                related = {}
                for issue in relatedissues:
                    related[issue] = {'repo':root,
                                      'title':issues[issue]['title']}
                diff['relatedissues'] = related
            diffs += repodiffs
            
        c.css = '<style type="text/css">%s</style>' % HtmlFormatter().get_style_defs('.highlight')
        c.diffs = diffs
        return render('dv/commit.html')

    def commit(self):
        """Use the list of files given by the user to commit to the repository"""
        # The variable passing schema we use means that we'll have problems
        # with a repository named 'on'.  We should look into a fix for that.
        url = request.environ['routes.url']

        # We send out a form with two inputs per file, one hidden with the
        # repository, and one checkbox.  We get back two values for the file if
        # the checkbox is checked, and one otherwise.  It's not perfect, but it
        # works for now.
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
                files = (repochroot(path.join(repo.root, file)) for file in changeset[root])
            except IOError:
                error = 'Bad Filename'
                redirect(url.current(action='index', error=error))
            commands.commit(self.ui, repo, message=message, logfile=None, *files)
        redirect(url.current(action='index'))

    def revert(self):
        """Revert the given file to its pristine state."""
        # The variable passing schema we use means that we'll have problems
        # with a repository named 'on'.  We should look into a fix for that.
        # TODO Make this get require a post and spit back a confirmation form
        url = request.environ['routes.url']

        repo = request.params['repo']
        filename = request.params['filename']

        if not repo or not filename:
            redirect(url.current(action='index'))

        found = False
        for repoobj, root in self.repositories:
            if root == repo:
                found = True
                repo = repoobj
                break
        if not found:
            redirect(url.current(action='index'))
        repochroot = Chroot(repo.root)
        try:
            filepath = repochroot(path.join(repo.root, filename))
        except IOError:
            error = 'Bad Filename'
            redirect(url.current(action='index', error=error))
        # repo.status() returns a tuple of lists, each lists containing the
        # files containing a given status.  Those are:
        # modified, added, removed, deleted, unknown, ignored, clean
        modified, added, removed, deleted, unknown, ignored, clean = repo.status()
        for status in [modified, added, removed, deleted]:
            if filename in status:
                commands.revert(self.ui, repo, filepath, rev='tip', date=None)
        redirect(url.current(action='index'))
