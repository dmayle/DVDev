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

"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_genshi as render

from pylons import request, response, session, tmpl_context as c

from pylons import config
from mercurial import commands, ui, hg
from filesafe import get_sanitized_path
from os import makedirs, path

repositories = config.get('repo').split()

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""

        # Perform repository setup
        self.ui = ui.ui()
        # Handle the user and add it to the call
        identity = request.environ.get('repoze.who.identity')
        if identity:
            self.user = identity.get('repoze.who.userid')
            workspace = self.__ensure_repositories()
            self.repositories = [(hg.repository(self.ui, path.join(workspace, path.basename(repo))), path.basename(repo)) for repo in repositories]
        else:
            self.repositories = [(hg.repository(self.ui, repo), path.basename(repo)) for repo in repositories]
        c.uncommitted = ''
        for repo, name in self.repositories:
            self.ui.pushbuffer()
            commands.diff(self.ui, repo)
            test = self.ui.popbuffer()
            if test:
                c.uncommitted = 'uncommitted'
                break
        # Make the repo available to the template
        c.project = environ['pylons.routes_dict'].get('repository')
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

    def __ensure_repositories(self):
        workspace = get_sanitized_path(config.get('workspace').split('/') + [self.user])
        try:
            makedirs(workspace)
        except OSError:
            pass
        for repo in repositories:
            if not path.exists(path.join(workspace, path.basename(repo))):
                commands.clone(self.ui, repo, path.join(workspace, path.basename(repo)))
        self.workspace = workspace
        return workspace
