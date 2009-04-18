"""Pylons middleware initialization"""
from beaker.middleware import CacheMiddleware, SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
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


from dvdev.config.environment import load_environment
import os
from repoze.who.config import make_middleware_with_config as make_who_with_config

# All sorts of repoze.who symbols.
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.openid import OpenIdIdentificationPlugin


from repoze.who.classifiers import default_request_classifier
from repoze.who.classifiers import default_challenge_decider




def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp()

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
    auth_tkt = AuthTktCookiePlugin(')h,&xCWlS}+u:<yD]BJV', 'auth_tkt')
    openid = OpenIdIdentificationPlugin('file', # 'mem'
            openid_field = 'openid',
            error_field = 'error',
            session_name = 'beaker.session',
            login_form_url = '/login_form',
            login_handler_path = '/do_login',
            logout_handler_path = '/logout',
            store_file_path = os.path.join(config['reporoot'], 'sstore'),
            logged_in_url = '/success',
            logged_out_url = 'logout_success',
            came_from_field = 'came_from',
            rememberer_name = 'auth_tkt',
            sql_associations_table = '',
            sql_nonces_table = '',
            sql_connstring = ''
            )

    identifiers = [('openid', openid),('auth_tkt',auth_tkt)]
    authenticators = [('openid', openid)]
    challengers = [('openid', openid)]
    mdproviders = []
    log_stream = None
    if config.get('WHO_LOG'):
        log_stream = sys.stdout

    app = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider,
        log_stream = log_stream,
        log_level=app_conf['who.log_level']
        )
    # app = make_who_with_config(app, global_conf, app_conf['who.config_file'], app_conf['who.log_file'], app_conf['who.log_level'])

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'])
        app = Cascade([static_app, app])

    return app
