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
    map.connect('/source/{path_info:.*}', controller='mercurialgateway')

    # Wiki routes allow us to get the url parts as a single variable
    map.connect('/wiki', controller='wiki', action='view', repository=repoid, path_info='')
    map.connect('/wiki/', controller='wiki', action='view', repository=repoid, path_info='')
    map.connect('/wiki/{path_info:.*}', controller='wiki', repository=repoid, action='view')
    map.connect('/{repository}/wiki', controller='wiki', action='view', path_info='')
    map.connect('/{repository}/wiki/', controller='wiki', action='view', path_info='')
    map.connect('/{repository}/wiki/{path_info:.*}', controller='wiki', action='view')

    map.connect('/login', controller='openiduser', action='login')
    map.connect('/success', controller='openiduser', action='success')

    map.connect('/', repository=repoid, controller=default_controller, action='index')
    map.connect('/{repository}', controller=default_controller, action='index')
    map.connect('/{repository}/{controller}', action='index')
    map.connect('/{repository}/{controller}/{action}')
    map.connect('/{repository}/{controller}/{action}/{id}')

    return map
