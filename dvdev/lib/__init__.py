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

from os import path

from re import compile
INVALID_FILE_CHARS = compile(r'[?%*:|"<>/]')

def get_sanitized_path(pathlist):
    """Turn a list of path elements into a path, while sanitizing the characters"""
    return path.join(*[INVALID_FILE_CHARS.sub('_', subpath) for subpath in pathlist])
