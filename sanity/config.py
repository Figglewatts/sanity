import yaml
import sanity.associations

REQUIRED_KEYS = [
    "checker_dir"
]

DEFAULT_ASSOCIATION = [
    {"^.*$": ["^.*$"]}
]

class Config:
    """Config stores parsed values from the config YAML file.

    Args:
        config_yaml (dict): Parsed YAML config file.

    Attributes:
        checker_dir (str): The directory of checker modules to use.
        associations (arr[dict[str, arr[str]]]): Associations between filenames
            and checkers to run against them. An array of dicts mapping filenames to
            names of checkers to run against this filename. Supports regexes for
            both filenames and checker names, simply enclose regex in '^' and '$'.
    """
    def __init__(self, config_yaml):
        self.checker_dir = config_yaml["checker_dir"]
        associations = config_yaml.get("file_checker_associations", DEFAULT_ASSOCIATION)
        try:
            self.associations = sanity.associations.compile_associations(associations)
        except sanity.associations.AssociationError as exc:
            raise ConfigError("Unable to load associations:", exc)
            

class ConfigError(Exception):
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