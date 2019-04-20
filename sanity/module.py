import importlib
import importlib.util
import inspect
from os import listdir
from os.path import isfile, join, splitext, exists

VALID_MODULE_EXTENSIONS = [
    ".py"
]
"""The file extensions valid for a checker module."""

IGNORE_MODULE_NAMES = [
    "__init__.py"
]
"""File names to be ignored when loading modules from a directory."""

DESIRED_CHECK_ARGSPEC = inspect.ArgSpec(args=['path', 'params'], varargs=None, keywords=None, defaults=None)
"""The desired signature of a check() function in a checker module."""

def validate_checker_function(checker_func):
    # check first to see if it's actually a function
    if not callable(checker_func):
        return False

    # now check to see if it has the right signature
    spec = inspect.getargspec(checker_func)
    if spec != DESIRED_CHECK_ARGSPEC:
        return False

    return True

def load_checker_function(module):
    try:
        checker_func = getattr(module, "check")
        if not validate_checker_function(checker_func):
            raise ImportError(f"Module {module.__file__} check() function malformed!"
                              " Expected 'def check(directory):'")
        return checker_func
    except AttributeError:
        raise ImportError(f"Module {module.__file__} did not have check() function!")

def load_checker_module(module_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return load_checker_function(module)

def load_checker_modules(directory):
    if not exists(directory):
        raise ValueError(f"Directory '{directory}' did not exist!")

    checkers = {}

    for file in [f for f in listdir(directory) if isfile(join(directory, f))]:
        filename, ext = splitext(file)
        if ext in VALID_MODULE_EXTENSIONS and file not in IGNORE_MODULE_NAMES:
            func = load_checker_module(join(directory, file), filename)
            checkers[filename] = func

    return checkers