import re

DEFAULT_FILENAME_PATTERN = "^.*$"

def check(path, params):
    filename_pattern_param = params.get("filename_pattern", DEFAULT_FILENAME_PATTERN)
    filename_pattern = re.compile(filename_pattern_param)
    if filename_pattern.match(path):
        return True, ""
    else:
        return False, f"{path} did not match pattern '{params['filename_pattern']}'"