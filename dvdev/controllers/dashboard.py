import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from dvdev.lib.base import BaseController

log = logging.getLogger(__name__)

class DashboardController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/dashboard.mako')
        # or, return a response
        return 'Hello World'
