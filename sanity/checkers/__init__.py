"""This package contains several example checkers that can be used as inspiration
for your own checkers.

It also contains code that is common to a lot of the checkers implemented.

Author:
    Sam Gibson <samolivergibson@gmail.com>
"""

from os import listdir
from os.path import isfile, join

def list_files(directory):
    """Get a list of all files in a directory."""
    return [name for name in listdir(directory) if isfile(join(directory, name))]