import os
from dvdev.config.middleware import make_app
from paste.httpserver import serve
from tempfile import NamedTemporaryFile
from mercurial import hg, ui, util
from mercurial.error import RepoError

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
    
    print "All repositories: %r" % filter(None, flatten(build_repo_tree()))
    config = {
        'use': 'egg:DVDev',
        'full_stack': 'true',
        'static_files': 'true',

        'reporoot': os.getcwd(),
        'cache_dir': os.path.join(os.getcwd(), 'data'),
        'beaker.session.key': 'dvdev',
        'beaker.session.secret': 'somesecret',

        'repo': ' '.join(filter(None, flatten(build_repo_tree()))),
        'project_home': 'issues',
        'who.log_level': 'debug',
        'who.log_file': 'stdout',
        'workspace': os.path.join(os.getcwd(), 'workspace'),
    }
    app = make_app({'debug': 'true'}, **config)
    serve(app, host='0.0.0.0', port=3000)

if __name__ == '__main__':
    main()
