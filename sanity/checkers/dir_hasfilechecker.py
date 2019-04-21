"""Check to see if a given list of files is present in a directory.

Parameters:
    files_list (list[str]): The list of files that need to be present.
"""

from os import listdir
from os.path import isfile, join

from sanity.checkers import list_files

DEFAULT_FILES_LIST = []

def check(path, params):
    files_list_param = params.get("files_list", DEFAULT_FILES_LIST)
    file_list = list_files(path)
    for f in files_list_param:
        if f not in file_list:
            return False, f"file '{f}' was not in directory."
    return True, ""
