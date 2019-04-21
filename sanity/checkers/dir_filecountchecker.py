"""Check to see if the file count of a directory is within a given range.

Parameters:
    max_file_count (int): The max number of files allowed in the directory.
        Set to -1 to disable this check.
    min_file_count (int): The min number of files allowed in the directory.
        Set to -1 to disable this check.
"""

from os import listdir
from os.path import isfile, join

from sanity.checkers import list_files

DEFAULT_MAX_FILE_COUNT = 10
DEFAULT_MIN_FILE_COUNT = 1

def get_file_count(directory):
    return len(list_files(directory))

def check(path, params):
    max_filecount_param = params.get("max_file_count", DEFAULT_MAX_FILE_COUNT)
    min_filecount_param = params.get("min_file_count", DEFAULT_MIN_FILE_COUNT)
    filecount = get_file_count(path)
    
    if min_filecount_param != -1:
        if filecount < min_filecount_param:
            return False, f"file count did not exceed minimum: '{min_filecount_param}', found: {filecount}"
        
    if max_filecount_param != -1:
        if filecount > max_filecount_param:
            return False, f"file count exceeded max: '{max_filecount_param}', found: {filecount}"

    return True, ""