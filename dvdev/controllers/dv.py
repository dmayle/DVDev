# DVDev - Distributed Versioned Development - tools for Open Source Software
# Copyright (C) 2009  Douglas Mayle

# This file is part of DVDev.

# DVDev is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# DVDev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with DVDev.  If not, see <http://www.gnu.org/licenses/>.

import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from dvdev.lib.base import BaseController, render
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter
from mercurial import commands, ui, hg, patch, cmdutil
from re import compile
from os import path, unlink
from filesafe import Chroot
from pylons.decorators import rest
import yamltrak

# Regex to pull the filename out of the diff header
DIFF_FILE = compile(r'diff -r [0-91-f]+ (.*)$')

log = logging.getLogger(__name__)

class DvController(BaseController):

    def index(self):
        """Go through all of the repositories and list any uncommitted changes"""
            
        c.css = '<style type="text/css">%s</style>' % HtmlFormatter().get_style_defs('.highlight')
        c.diffs = self._get_diffs()
        return render('dv/commit.html')

    def _get_diffs(self, repository=None, filepath=None):
        diffs = []
        for repo, root in self.repositories:
            if repository and root != repository:
                continue
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
                if filepath and filepath == filename:
                    return {'repository':root,
                            'filename':filename,
                            'diff': highlight(diff, DiffLexer(), HtmlFormatter())}
                # Should I instantiate a single lexer and formatter and share them?
                repodiffs.append({'repository':root,
                               'filename':filename,
                               'diff': highlight(diff, DiffLexer(), HtmlFormatter())})
            # At the repo level, we want to go through all found files and look
            # for related issues
            try:
                issues = yamltrak.issues([repo.root])[root]
            except KeyError:
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
        # Done collecting the diffs
        if filepath:
            # User wanted a specific diff, and we didn't find it.  This
            # probably isn't the best exception, but it will have to do...
            raise LookupError

        return diffs

    @rest.dispatch_on(GET='index')
    def commit(self):
        """Use the list of files given by the user to commit to the repository"""
        # The variable passing schema we use means that we'll have problems
        # with a repository named 'on'.  We should look into a fix for that.
        url = request.environ['routes.url']

        # We send out a form with two inputs per file, one hidden with the
        # repository, and one checkbox.  We get back two values for the file if
        # the checkbox is checked, and one otherwise.  It's not perfect, but it
        # works for now.
        message = request.params['message']
        if not message:
            redirect(url.current(action='index'))
        for repo, root in self.repositories:
            if root not in request.params:
                continue
            repochroot = Chroot(repo.root)
            try:
                files = (repochroot(path.join(repo.root, file)) for file in request.params.getall(root))
            except IOError:
                error = 'Bad Filename'
                redirect(url(controller='dv', action='index', error=error))
            self.ui.pushbuffer()
            commands.commit(self.ui, repo, message=message, logfile=None, *files)
            output = self.ui.popbuffer()
        redirect(url.current(action='index'))

    @rest.dispatch_on(POST='_revert_confirmed')
    def revert(self, repository, filepath):
        url = request.environ['routes.url']

        if not repository or not filepath:
            redirect(url.current(action='index'))

        found = False
        for repoobj, root in self.repositories:
            if root == repository:
                found = True
                repo = repoobj
                break
        if not found:
            # Better error handling? Raise a 404, I guess... Maybe handle this
            # in lib/base ???
            redirect(url.current(action='index'))

        repochroot = Chroot(repo.root)
        try:
            fullfilepath = repochroot(path.join(repo.root, filepath))
        except IOError:
            error = 'Bad Filename'
            redirect(url.current(action='index', error=error))
        # repo.status() returns a tuple of lists, each lists containing the
        # files containing a given status.  Those are:
        # modified, added, removed, deleted, unknown, ignored, clean
        statusmapper = dict(enumerate(['modified', 'added', 'removed', 'deleted', 'unknown', 'ignored', 'clean']))

        c.added = False
        statuses = repo.status()
        for index, status in statusmapper.iteritems():
            if filepath in statuses[index]:
                c.status = status
                if status == 'added':
                    c.added = True
                break

        c.filepath = filepath
        try:
            c.diff = self._get_diffs(repository=repository, filepath=filepath)
        except LookupError:
            redirect(url.current(action='index', error='File not in repository'))
            
        c.css = '<style type="text/css">%s</style>' % HtmlFormatter().get_style_defs('.highlight')
        return render('dv/revert.html')

    def _revert_confirmed(self, repository, filepath):
        """Revert the given file to its pristine state."""
        # The variable passing schema we use means that we'll have problems
        # with a repository named 'on'.  We should look into a fix for that.
        # TODO Make this get require a post and spit back a confirmation form
        url = request.environ['routes.url']

        if not repository or not filepath:
            redirect(url.current(action='index'))

        found = False
        for repoobj, root in self.repositories:
            if root == repository:
                found = True
                repo = repoobj
                break
        if not found:
            redirect(url.current(action='index'))
        repochroot = Chroot(repo.root)
        try:
            fullfilepath = repochroot(path.join(repo.root, filepath))
        except IOError:
            error = 'Bad Filename'
            redirect(url.current(action='index', error=error))
        # repo.status() returns a tuple of lists, each lists containing the
        # files containing a given status.  Those are:
        # modified, added, removed, deleted, unknown, ignored, clean
        statusmapper = dict(enumerate(['modified', 'added', 'removed', 'deleted', 'unknown', 'ignored', 'clean']))

        statuses = repo.status()
        for index, status in statusmapper.iteritems():
            if status not in ['modified', 'added', 'removed', 'deleted']:
                # Unknown, ignored, and clean files can't be reverted...
                if filepath in statuses[index]:
                    c.status = status
                    c.error = "Can't revert this file"
                    return render('dv/revert.html')
                continue
            if filepath in statuses[index]:
                commands.revert(self.ui, repo, fullfilepath, rev='tip', date=None)
                if status == 'added' and request.params.get('remove'):
                    unlink(fullfilepath)
                redirect(url(repository=repository, controller='dv', action='index'))

        c.error = 'Not found'
        return render('dv/revert.html')
