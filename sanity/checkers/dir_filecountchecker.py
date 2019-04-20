"""Check to see if the file count of a directory exceeds a certain value."""

from os import listdir
from os.path import isfile, join

DEFAULT_MAX_FILE_COUNT = 10

def get_file_count(directory):
    return len([name for name in listdir(directory) if isfile(join(directory, name))])

def check(path, params):
    max_filecount_param = params.get("max_file_count", DEFAULT_MAX_FILE_COUNT)
    filecount = get_file_count(path)
    if filecount > max_filecount_param:
        return False, f"file count exceeded max: '{max_filecount_param}', found: {filecount}"
    else:
        return True, ""