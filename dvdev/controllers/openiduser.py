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

from pylons import config
from os import path, makedirs
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

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
