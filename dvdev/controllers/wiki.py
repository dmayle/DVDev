from __future__ import with_statement
import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from dvdev.lib.base import BaseController, render
from pylons import config
from os import path
from docutils.core import publish_parts
from pylons.decorators import rest

log = logging.getLogger(__name__)

repositories = dict((repo.split(path.sep)[-1], repo) for repo in config.get('repo').split())

class WikiController(BaseController):

    @rest.dispatch_on(POST='edit')
    def view(self, repository, wikipath):
        # Return a rendered template
        #return render('/wiki.mako')
        # or, return a response
        url = request.environ['routes.url']
        default_root = config.get('wiki_root','docs')
        default_page = config.get('wiki_home','README.txt')
        if not wikipath:
            wikipath = default_page
        try:
            with open(path.join(repositories[repository], wikipath)) as page:
                c.page_text = page.read()
        except IOError, e:
            # File not found error
            if e.args[0] == 2:
                redirect('/%s/wiki/new/%s' % (c.project, wikipath))
            redirect('/%s/wiki/new/%s' % (c.project, wikipath))
                
        c.page_html = publish_parts(c.page_text, writer_name='html', settings_overrides={'report_level':5})
        return render('wiki/page.html')

    @rest.dispatch_on(POST='_create')
    def new(self, repository, wikipath):
        # Return a rendered template
        #return render('/wiki.mako')
        # or, return a response
        url = request.environ['routes.url']
        default_root = config.get('wiki_root','docs')
        default_page = config.get('wiki_home','README.txt')
        if not wikipath:
            wikipath = default_page
        try:
            with open(path.join(repositories[repository], wikipath)) as page:
                pass
            # We can read, so we redirect to the page edit view
            redirect(url.current(action='view'))
        except IOError:
            pass
                
        return render('wiki/new.html')

    def edit(self, repository, wikipath):
        # Return a rendered template
        #return render('/wiki.mako')
        # or, return a response
        url = request.environ['routes.url']
        default_root = config.get('wiki_root','docs')
        default_page = config.get('wiki_home','README.txt')
        if not wikipath:
            wikipath = default_page
        c.page_text = request.params['page_text']
        with open(path.join(repositories[repository], wikipath), 'w') as page:
            page.write(c.page_text)
        redirect(url.current(action='view'))
