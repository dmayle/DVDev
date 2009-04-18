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
from pylons.controllers.util import abort, redirect_to

from dvdev.lib.base import BaseController, render

# This is the mercurial WSGI web server
from mercurial.hgweb.hgwebdir_mod import hgwebdir
from mercurial import ui, extensions
from pylons import config
from os import path

# We build a list of repositorie tuples consisting of the project name, and their directory
repositories = [(path.basename(repo), repo) for repo in config.get('repo').split()]

# Set some global config in a parent ui
parentui = ui.ui()
# Pylons already includes Pygments, so this comes for free!
extensions.load(parentui, 'hgext.highlight', '')

log = logging.getLogger(__name__)

class MercurialgatewayController(BaseController):

    def __call__(self, environ, start_response):
        application = hgwebdir(repositories, parentui)
        output = application(environ, start_response)
        return ''.join([x for x in output])

