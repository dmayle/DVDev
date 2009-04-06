#   DVDev - Distributed Versioned Development - tools for Open Source Software
#   Copyright (C) 2009  Douglas Mayle

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to, redirect
from pylons.decorators import rest

from dvdev.lib.base import BaseController, render

import yamltrak
from pylons import config
from os import path

repositories = dict((repo.split(path.sep)[-1], repo) for repo in config.get('repo').split())

log = logging.getLogger(__name__)

class IssuesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('issue', 'issues')

    def index(self, repository, format='html'):
        """GET /issues: All items in the collection"""
        # url('issues')
        # Read the config to find the repository source...
        # Need to figure out the ini file, the issues directory
        # I think YAMLTrak should be a package, not a webapp...
        c.issues = yamltrak.issues(repositories.values(), 'issues')
        return render('issues/index.html')

    def create(self, repository):
        """POST /issues: Create a new item"""
        # url('issues')

    @rest.dispatch_on(POST='_add_new')
    def new(self, repository, format='html'):
        """GET /issues/new: Form to create a new item"""
        skeleton = yamltrak.issue(repositories[repository], 'issues', 'skeleton', detail=False)
        c.skeleton = skeleton[0]['data']
        return render('issues/add.html')
        # url('new_issue')

    def _add_new(self, repository, format='html'):
        issue = {}
        issue['title'] = request.params.get('title')
        issue['description'] = request.params.get('description')
        issue['estimate'] = request.params.get('estimate')
        if not issue['title'] or not issue['description'] or not issue['estimate']:
            c.issue = issue
            return render('issues/add.html')
        issueid = yamltrak.add(repositories[repository], issue)
        url = request.environ['routes.url']
        redirect(url.current(repository=repository, id=issueid, action='show'))

    def update(self, repository, id):
        """PUT /issues/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('issue', id=ID),
        #           method='put')
        # url('issue', id=ID)

    def delete(self, repository, id):
        """DELETE /issues/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('issue', id=ID),
        #           method='delete')
        # url('issue', id=ID)

    def close(self, repository, id):
        """POST /issues/id: Show a specific item"""
        # url('issue', id=ID)
        if yamltrak.close(repositories[repository], id):
            redirect_to('/issues')
        redirect_to(action='show', id=id)

    def show(self, repository, id, format='html'):
        """GET /repository/issues/id: Show a specific item"""
        # url('issue', id=ID)
        c.id = id
        issue = yamltrak.issue(repositories[repository], 'issues', id)
        skeleton = yamltrak.issue(repositories[repository], 'issues', 'skeleton', detail=False)
        c.issue = issue[0]['data']
        c.skeleton = skeleton[0]['data']
        c.uncommitted_diff = issue[0].get('diff')
        c.versions = issue[1:]
        return render('issues/issue.html')

    @rest.dispatch_on(GET='show')
    def edit(self, repository, id, format='html'):
        """GET /issues/id/edit: Form to edit an existing item"""
        # url('edit_issue', id=ID)
        skeleton = yamltrak.issue(repositories[repository], 'issues', 'skeleton', detail=False)
        issue = {}
        for key in skeleton[0]['data']:
            if key in request.params:
                issue[key] = request.params[key]
        yamltrak.edit_issue(repositories[repository], 'issues', issue, id)
        redirect_to(action='show', id=id)
