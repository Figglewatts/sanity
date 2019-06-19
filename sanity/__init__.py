"""Perform sanity checks on directories of files.

sanity can dynamically load python modules from a directory and execute them
on a directory of files based on rules specified in a config file.

The modules loaded should define a function with the following signature::
    def check(path, params):

The check() function should return a 2-tuple containing:
    * A bool indicating whether or not the check was a success.
    * The reason for failure if the check failed, otherwise an empty string if
        the check was a success.

Example::
    # parse the config file
    conf = sanity.config.parse_config(config_file_path)

    # create a sanity checking context
    ctx = sanity.CheckerContext(conf, directory_path_to_check)

    # run the checks
    sanity.check(ctx, directory_path_to_check)

Author:
    Sam Gibson <samolivergibson@gmail.com>
"""

from os import listdir
from os.path import isfile, isdir, join, exists

from colorama import Fore, Style
import colorama

import sanity.rules
from sanity.moduleloader import load_checker_modules
from sanity.util import print_depth

class CheckerContext:
    """Encapsulates all data needed to check the sanity of a directory of files.

    Args:
        config (Config): The Config object parsed from the YAML file with 
            sanity.config.parse_config(...)
        directory (str): The directory containing the assets we want to check.

    Raises:
        ContextCreationError: if there was an error creating the checker context.

    Attributes:
        checkers (dict[str, func]): Maps checker names to check() functions as
            loaded from modules.
        file_rules (dict[str, FileCheckerRule]): Maps file name rule
            regexes to FileCheckerRule objects, storing compiled file name regexes
            and an array of compiled checker name regexes. To be used for running certain
            checkers on certain files.
        dir_rules (list[re.Pattern]): Stores the compiled regexes for figuring out
            which checkers to run on the entire directory.
        checker_params: A dictionary containing checker parameters. Maps checker names
            to dictionaries of parameter names/values.
        recursive (bool): Whether or not to recurse into subdirectories when checking sanity.
    """
    def __init__(self, config, directory):
        # try and load the checker modules from the directory in the loaded config
        try:
            self.checkers = load_checker_modules(config.checker_dir)
        except ValueError as exc:
            raise ContextCreationError(f"Could not load checker modules, {str(exc)}")
        except ImportError as exc:
            raise ContextCreationError(f"Could not load module, {str(exc)}")

        # try and load the file checker rules
        try:
            self.file_rules = sanity.rules.compile_file_rules(config.file_rules)
        except sanity.rules.RuleError as exc:
            raise ContextCreationError(f"Could not compile file rules, {str(exc)}")

        # try to load the directory checker rules
        try:
            self.dir_rules = sanity.rules.compile_directory_rules(config.dir_rules)
        except sanity.rules.RuleError as exc:
            raise ContextCreationError(f"Could not compile directory rules, {str(exc)}")

        self.checker_params = config.checker_params
        self.recursive = config.recursive

class ContextCreationError(Exception):
    """Raised by constructor of CheckerContext."""
    def __init__(self, reason):
        self.reason = reason
    
    def __str__(self):
        return f"{self.reason}"

def run_check(check_func, path, checker_name, checker_params):
    """Run a single check against a single target path (file or directory).

    Args:
        check_func (func): The checker function to call, loaded in from a checker
            module.
        path (str): The target path - gets passed into the checker function.
        checker_name (str): The name of this checker, used to identify the checker
            in output.
        checker_params (dict[str, value]): The params to pass to the checker function,
            these have been loaded in from the config file and are used to parameterise
            some of the variables in the checker modules.

    Returns:
        True if the check was a success, False otherwise.
    """
    # run the check function, passing in any required state, print and return the result
    result, reason = check_func(path, checker_params)
    if result is True:
        print_depth(f"[{Fore.GREEN}PASS{Style.RESET_ALL}] - {checker_name} on {path}", 2)
    else:
        print_depth(f"[{Fore.RED}FAIL{Style.RESET_ALL}] - {checker_name} on {path}, reason: {reason}", 2)
    return result

def process_checker(path, checker_regex, checkers, config_params):
    """Process a single checker rule. A checker rule is a regex that will match
    to any number of checker modules loaded from the checkers directory.

    Args:
        path (str): The path to what we're checking right now. Could be a file
            or a directory.
        checker_regex (re.Pattern): The compiled regex to match checker names
            against, to figure out which ones to run.
        checkers (dict[str, func]): The checkers loaded in from the checker modules
            directory.
        config_params (dict[str, dict[str, value]]): The params loaded from the config
            file.

    Returns:
        True if all the checks succeeded, False otherwise.
    """
    status = True
    for checker_name, checker_func in sanity.rules.filter_checkers(checkers, checker_regex):
        checker_params = config_params.get(checker_name, {})
        success = run_check(checker_func, path, checker_name, checker_params)
        
        # if at least one check failed we want to indicate this
        if not success:
            status = False
    return status
    
def process_file_rule(rule_name, file_rule, files, checkers, config_params):
    """Process a file rule parsed from the config file.

    Args:
        rule_name (str): The regex of the rule, to match against
            file names.
        file_rule (FileCheckerRule): The rule to run.
        files (list[str]): An unfiltered array of files in the assets directory.
        checkers (dict[str, func]): The loaded checker modules.
        config_params (dict[str, dict[str, value]]): The params loaded from the config
            file.

    Returns:
        True if all the checks succeeded, False otherwise.
    """
    print_depth(f"Processing file rule: '{rule_name}'", 1)
    status = True
    # filter out which files we care about based on the rule
    for file in sanity.rules.filter_files(files, file_rule.file_name):
        # process each regex in the rule
        for checker_regex in file_rule.checker_names:
            success = process_checker(file, checker_regex, checkers, config_params)
            # if at least one check failed we want to indicate this
            if not success:
                status = False
    return status

def check_on_directory(context, directory):
    """Perform a sanity check on a given directory.

    Args:
        context (CheckerContext): The context to use. Cannot be None.
        directory (str): The directory to check the sanity of. Files and directories
            within will be checked.

    Returns:
        True if all checks passed, False otherwise.
    """
    print_depth(f"Performing sanity checks in directory: {directory}")

    # run the directory checks
    directory_check_result = True
    if len(context.dir_rules) > 0:
        print_depth(f"Processing checks for directory: {directory}", 1)
        # for all of the given directory checker regexes, process them
        for dir_check_regex in context.dir_rules:
            success = process_checker(directory, dir_check_regex, context.checkers, context.checker_params)
            # if any check fails we want to show this
            if not success:
                directory_check_result = False
        if directory_check_result:
            print_depth(f"{Fore.GREEN}Directory checks PASSED on {directory}!{Style.RESET_ALL}", 1)
        else:
            print_depth(f"{Fore.RED}Directory checks FAILED on {directory}.{Style.RESET_ALL}", 1)

    # get the asset files we want to check
    files_in_dir = [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
    
    # for all of the given file rules, run the associated checks
    file_check_result = True
    for rule_name, file_rule in context.file_rules.items():
        success = process_file_rule(rule_name, file_rule, files_in_dir, 
                                           context.checkers, context.checker_params)
        # if any check fails we want to show this
        if not success:
            file_check_result = False
    if file_check_result:
        print_depth(f"{Fore.GREEN}File checks PASSED in {directory}!{Style.RESET_ALL}", 1)
    else:
        print_depth(f"{Fore.RED}File checks FAILED in {directory}.{Style.RESET_ALL}", 1)

    # check to see if we should recurse into subdirectories
    recursive_result = True
    if (context.recursive):
        dirs_in_dir = [d for d in listdir(directory) if isdir(join(directory, d))]

        for d in dirs_in_dir:
            new_dir_path = join(directory, d)
            success = check_on_directory(context, new_dir_path)
            if not success:
                recursive_result = False

    return directory_check_result and file_check_result and recursive_result


def check(context, directory):
    """Check the given directory for sanity using the provided context.
    
    Directory must exist, and context cannot be None.
    """
    # init colorama for Windows terminal color support
    colorama.init()

    # perform the checks
    success = check_on_directory(context, directory)

    # output the result
    if success:
        print_depth(f"{Fore.GREEN}All checks PASSED!{Style.RESET_ALL}")
    else:
        print_depth(f"{Fore.RED}Some checks FAILED.{Style.RESET_ALL}")