"""Defines functions for loading python modules, extracting check() functions,
and checking to see whether or not they are valid.

Author:
    Sam Gibson <samolivergibson@gmail.com>
"""

import importlib
import importlib.util
import inspect
from os import listdir
from os.path import isfile, join, splitext, exists

VALID_MODULE_EXTENSIONS = [
    ".py"
]
"""list[str]: The file extensions valid for a checker module."""

IGNORE_MODULE_NAMES = [
    "__init__.py"
]
"""list[str]: File names to be ignored when loading modules from a directory."""

DESIRED_CHECK_ARGSPEC = inspect.ArgSpec(args=['path', 'params'], varargs=None, keywords=None, defaults=None)
"""inspect.ArgSpec: The desired signature of a check() function in a checker module."""

def validate_checker_function(checker_func):
    """Check to see if a loaded check() function has the correct signature."""
    # check first to see if it's actually a function
    if not callable(checker_func):
        return False

    # now check to see if it has the right signature
    spec = inspect.getargspec(checker_func)
    if spec != DESIRED_CHECK_ARGSPEC:
        return False

    return True

def load_checker_function(module):
    """Load a checker function from a loaded module.

    Args:
        module (types.ModuleType): The loaded module.

    Raises:
        ImportError: if the function had the wrong signature or was not present.
    """
    try:
        # try getting the check attribute, and make sure it's a function with the correct signature
        checker_func = getattr(module, "check")
        if not validate_checker_function(checker_func):
            raise ImportError(f"Module {module.__file__} check() function malformed!"
                              " Expected 'def check(directory):'")
        return checker_func
    except AttributeError:
        raise ImportError(f"Module {module.__file__} did not have check() function!")

def load_checker_module(module_path, module_name):
    """Try loading a checker module from a path.

    Args:
        module_path (str): The path to the module to load.
        module_name (str): The name of the module to load.

    Raises:
        ImportError: If the module was malformed in any way.

    Returns:
        func: The check() function of the loaded module.
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return load_checker_function(module)

def load_checker_modules(directory):
    """Load all modules present in a given directory.

    Args:
        directory (str): The path to the directory to load from.

    Raises:
        ValueError: If the given directory did not exist.
        ImportError: If the imported module was malformed in any way.

    Returns:
        dict[str, func]: Maps module names to their loaded check() functions.
    """
    # first check if the directory exists
    if not exists(directory):
        raise ValueError(f"Directory '{directory}' did not exist!")

    checkers = {}

    # now load every .py file in the directory's check() function
    for file in [f for f in listdir(directory) if isfile(join(directory, f))]:
        filename, ext = splitext(file)
        # check to see if this file is valid for loading
        if ext in VALID_MODULE_EXTENSIONS and file not in IGNORE_MODULE_NAMES:
            func = load_checker_module(join(directory, file), filename)
            checkers[filename] = func

    return checkers