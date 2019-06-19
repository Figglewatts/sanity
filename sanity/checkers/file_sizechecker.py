"""File size checker. Checks to see if a file size is within a certain range.

Parameters:
    min_size (int): The minimum file size acceptable (in bytes). Set to -1 to disable.
    max_size (int): The maximum file size acceptable (in bytes). Set to -1 to disable.
"""

from os.path import getsize

DEFAULT_MIN_SIZE = -1
DEFAULT_MAX_SIZE = -1

def check(path, params):
    min_size = params.get("min_size", DEFAULT_MIN_SIZE)
    max_size = params.get("max_size", DEFAULT_MAX_SIZE)
    file_size = getsize(path)
    if min_size != -1:
        if file_size < min_size:
            return False, f"file size '{file_size}' byte(s) was smaller than minimum '{min_size}'"

    if max_size != -1:
        if file_size > max_size:
            return False, f"file size '{file_size}' byte(s) was bigger than maximum '{max_size}'"

    return True, ""