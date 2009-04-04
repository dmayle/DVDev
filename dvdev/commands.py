import os
from tempfile import NamedTemporaryFile

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
    if maxdepth < 1:
        return
    """Build a tree structure that represents the loaded repositories."""
    # Check to see if the current directory is a repo.  If so, use that.
    if True:
        return path.abspath(root)

    # I'm feeling lazy, so I think I'm gonna do this recursively with a
    # maxdepth. For each subdirectory of the current, check to see if it's a
    # repo.
    return [build_repo_tree(subpath, maxdepth-1) for subpath in os.listdir(root)]

def main():
    
    print "hello world"

if __name__ == '__main__':
    main()
