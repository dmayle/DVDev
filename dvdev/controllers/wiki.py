from __future__ import with_statement
import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from dvdev.lib.base import BaseController, render
from pylons import config
from os import path
from docutils.core import publish_parts
from pylons.decorators import rest

log = logging.getLogger(__name__)

repositories = dict((repo.split(path.sep)[-1], repo) for repo in config.get('repo').split())

class WikiController(BaseController):

    @rest.dispatch_on(POST='edit')
    def view(self, repository, path_info):
        # Return a rendered template
        #return render('/wiki.mako')
        # or, return a response
        default_page = config.get('wiki_home','README')
        if not path_info:
            path_info = default_page
        with open(path.join(repositories[repository], path_info)) as page:
            c.page_text = page.read()
        c.page_html = publish_parts(c.page_text, writer_name='html', settings_overrides={'report_level':5})
        return render('wiki/page.html')

    def edit(self, repository, path_info):
        # Return a rendered template
        #return render('/wiki.mako')
        # or, return a response
        default_page = config.get('wiki_home','README')
        if not path_info:
            path_info = default_page
        c.page_text = request.params['page_text']
        with open(path.join(repositories[repository], path_info), 'w') as page:
            page.write(c.page_text)
        redirect_to(str('/wiki/%s/%s' % (repository, path_info)))
