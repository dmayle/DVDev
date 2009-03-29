from os import path

from re import compile
INVALID_FILE_CHARS = compile(r'[?%*:|"<>/]')

def get_sanitized_path(pathlist):
    """Turn a list of path elements into a path, while sanitizing the characters"""
    return path.join(*[INVALID_FILE_CHARS.sub('_', subpath) for subpath in pathlist])
