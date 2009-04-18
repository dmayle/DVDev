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

"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper
from os import path

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    # map.resource('issue', 'issues')

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # Get the default repository information from config
    default_repo = config.get('repo','').split()[0]
    default_controller = config.get('project_home','').split()[0]
    repoid = default_repo.split(path.sep)[-1]

    # CUSTOM ROUTES HERE
    map.connect('/source', controller='mercurialgateway', path_info='')
    map.connect('source', '/source/{path_info:.*}', controller='mercurialgateway')

    # Wiki routes allow us to get the url parts as a single variable
    map.connect('/wiki', controller='wiki', action='view', repository=repoid, wikipath='')
    map.connect('/wiki/', controller='wiki', action='view', repository=repoid, wikipath='')
    map.connect('/wiki/{action}/*wikipath', controller='wiki', repository=repoid, action='view')
    map.connect('/{repository}/wiki', controller='wiki', action='view', wikipath='')
    map.connect('/{repository}/wiki/', controller='wiki', action='view', wikipath='')
    map.connect('wiki', '/{repository}/wiki/{action}/*wikipath', controller='wiki', action='view', wikipath='')

    map.connect('/login', controller='openiduser', action='login')
    map.connect('/success', controller='openiduser', action='success')

    # Special mapping for revert confirmation
    map.connect('/{repository}/dv/revert/*filepath', controller='dv', action='revert')

    map.connect('/', repository=repoid, controller=default_controller, action='index')
    map.connect('/{repository}', controller=default_controller, action='index')
    map.connect('/{repository}/{controller}', action='index')
    map.connect('/{repository}/{controller}/{action}')
    map.connect('/{repository}/{controller}/{action}/{id}')

    return map
