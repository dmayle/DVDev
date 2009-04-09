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

import os
from dvdev.config.middleware import make_app
from paste.httpserver import serve
from tempfile import NamedTemporaryFile
from mercurial import hg, ui, util, commands
from mercurial.error import RepoError
from urllib2 import URLError
import webbrowser
from argparse import ArgumentParser

def build_config():
    """\
    Build a temporary config file to pass to paster so the user doesn't need
    to do this themselves. For the moment, this only works on Unix-like
    systems."""
    # Don't close this file, because it will disappear.  Instead, maybe we can
    # reopen it in readonly mode???
    config_tmp = NamedTemporaryFile()

    # Do stuff
    config_tmp.write('stuff')

    # This little dance ensures that the data is available to other programs,
    # thank you python docs (for the os module.)
    config_tmp.flush()
    os.fsync(config_tmp)

    return config_tmp

def build_repo_tree(root=os.getcwd(), maxdepth=2):
    """Build a tree structure that represents the loaded repositories."""
    if maxdepth < 1 or not os.path.isdir(root):
        return
    if os.path.basename(root) in ['sstore', 'data']:
        # Sorry guys, gotta do this for speed... The next step is to check for
        # .hg directories before trying to create the repo object.
        return
    # Check to see if the current directory is a repo.  If so, use that.
    myui = ui.ui()
    try:
        repo = hg.repository(myui, root)
    except RepoError:
        # I'm feeling lazy, so I think I'm gonna do this recursively with a
        # maxdepth. For each subdirectory of the current, check to see if it's
        # a repo.
        return [build_repo_tree(subpath, maxdepth-1) for subpath in os.listdir(root)]
    except util.Abort:
        # I'm feeling lazy, so I think I'm gonna do this recursively with a
        # maxdepth. For each subdirectory of the current, check to see if it's
        # a repo.
        if os.path.basename(root) in ['sstore', 'data']:
            return
        return [build_repo_tree(subpath, maxdepth-1) for subpath in os.listdir(root)]

    return os.path.abspath(root)


def flatten(lst):
    """\
    Temp function to flatten the nested lists. At some point, the repos will be
    in dictionaries that mirror the directory's tree structure."""
    output = []
    try:
        if not isinstance(lst, basestring):
            for elem in lst:
                output += flatten(elem)
        else:
            return [lst]
        return output
    except TypeError:
        return [lst]

def main():
    
    parser = ArgumentParser(description="DVDev: Distributed Versioned Development")
    parser.add_argument(
        'repositories', metavar='repository', type=str, nargs='*',
        default=[os.getcwd()], help='List of repositories to serve. If left '\
        'blank, DVDev will search the current and subdirectories for '\
        'existing repositories.')
    args = parser.parse_args()
    for index, repository in enumerate(args.repositories):
        if os.path.exists(repository):
            continue
        # Maybe this is a repository URL that mercurial recognizes?
        myui = ui.ui()
        myui.pushbuffer()

        try:
            commands.clone(myui, repository)
        except RepoError:
            print "Bad repository: %s" % repository
            import sys
            sys.exit(1)
        except URLError:
            print "Bad repository: %s" % repository
            import sys
            sys.exit(1)

        destination = myui.popbuffer().split('\n')[0]
        destination = destination.split('destination directory: ')[1]

        if not os.path.exists(destination):
            print "Successfully cloned repository %s but unable to read "\
            "local copy at %s" % (repository, destination)
            import sys
            sys.exit(1)

        # Update our repository list with the new local copy
        args.repositories[index] = destination

    all_repos = filter(None, flatten([build_repo_tree(repo) for repo in args.repositories]))
    print "All repositories: %r" % all_repos
    config = {
        'use': 'egg:DVDev',
        'full_stack': 'true',
        'static_files': 'true',

        'reporoot': os.getcwd(),
        'cache_dir': os.path.join(os.getcwd(), 'data'),
        'beaker.session.key': 'dvdev',
        'beaker.session.secret': 'somesecret',

        'repo': ' '.join(all_repos),
        'project_home': 'issues',
        'who.log_level': 'debug',
        'who.log_file': 'stdout',
        'workspace': os.path.join(os.getcwd(), 'workspace'),
    }
    app = make_app({'debug': 'true'}, **config)
    port = 4000
    webbrowser.open('http://localhost:%d/' % port)
    serve(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
