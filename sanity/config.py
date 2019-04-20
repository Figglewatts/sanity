"""Defines the Config class, as well as functions related parsing and
validating a YAML config file.

Author:
    Sam Gibson <samolivergibson@gmail.com>
"""

import yaml
import sanity.rules

REQUIRED_KEYS = [
    "checker_dir"
]
"""str: The keys in the YAML config file that are required. An exception will be thrown
when loading the config file if any of these are not present."""

DEFAULT_FILE_RULES = [
    {"^.*$": ["^.*$"]}
]
"""list[dict[str, list[str]]]: Used if no rules are given. Runs all checkers for all files."""

DEFAULT_PARAMETERS = {}
"""dict[str, value]: Used if no parameters are given. Doesn't set anything."""

DEFAULT_DIRECTORY_RULES = []
"""list[str]: Used if no checks are given. Doesn't run any checks on the directory."""

class Config:
    """Config stores parsed values from the config YAML file.

    Args:
        config_yaml (dict): Parsed YAML config file.

    Attributes:
        checker_dir (str): The directory of checker modules to use.
        file_rules (list[dict[str, list[str]]]): Rules concerning filenames
            and checkers to run against them. An array of dicts mapping filenames to
            names of checkers to run against this filename. Supports regexes for
            both filenames and checker names, simply enclose regex in '^' and '$'.
        checker_params (dict): Allows variables in checkers to be set. Maps
            names of checkers to values to pass into their checker function.
        directory_rules (list[str]): An array of checker name regexes to run on
            the entire directory as opposed to individual files.
        recursive (bool): Whether or not to recurse to subdirs when checking sanity.
    """
    def __init__(self, config_yaml):
        self.checker_dir = config_yaml["checker_dir"]
        self.file_rules = config_yaml.get("file_rules", DEFAULT_FILE_RULES)
        self.checker_params = config_yaml.get("parameters", DEFAULT_PARAMETERS)
        self.dir_rules = config_yaml.get("directory_rules", DEFAULT_DIRECTORY_RULES)
        self.recursive = config_yaml.get("recursive", False)
            

class ConfigError(Exception):
    """ConfigError is raised when there is some error when loading a config file.

    It contains (config_err) the error that caused the ConfigError to be raised.
    """
    def __init__(self, message, config_err=None):
        self.message = message
        self.config_err = config_err
    
    def __str__(self):
        return f"{self.message} {' ' + str(self.config_err) if self.config_err else ''}"

def validate_config(config_yaml):
    """Validate a config YAML file by checking if all required keys are present.
    
    Args:
        config_yaml (dict): The parsed YAML config file.

    Returns:
        (bool, str): Bool indicates if YAML was valid config. If False, str
        contains the name of the missing key.
    """
    for key in REQUIRED_KEYS:
        if config_yaml.get(key) is None:
            return False, key
    return True, ""

def parse_config(yaml_file):
    """Parse a config YAML file to a Config object.

    Args:
        yaml_file (str): The path to the YAML config file.

    Returns:
        Config: An instance of Config populated with data from the YAML file.

    Raises:
        ConfigError: If the config file could not be loaded.
    """

    # first try loading and parsing the config file
    parsed_yaml_config = None
    try:
        with open(yaml_file, 'r') as config_file:
            parsed_yaml_config = yaml.safe_load(config_file)
    except yaml.YAMLError as exc:
        raise ConfigError("Unable to parse config file", exc)
    except OSError as exc:
        raise ConfigError("Unable to open config file", exc)

    # now check that it's valid
    valid, missing_key = validate_config(parsed_yaml_config)
    if not valid:
        raise ConfigError(f"File missing required key: {missing_key}")
    
    return Config(parsed_yaml_config)