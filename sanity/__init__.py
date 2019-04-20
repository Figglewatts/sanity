from os import listdir
from os.path import isfile, join, exists

from colorama import Fore, Style
import colorama

import sanity.associations
from sanity.util import print_depth

class CheckerContext:
    """Encapsulates all data needed to check the sanity of a directory of files.

    Args:
        config (Config): The Config object parsed from the YAML file with 
            sanity.config.parse_config(...)
        directory (str): The directory containing the assets we want to check.

    Attributes:
        checkers (dict[str, func]): Maps checker names to check() functions as
            loaded from modules.
        file_associations (dict[str, FileCheckerAssociation]): Maps file name association
            regexes to FileCheckerAssociation objects, storing compiled file name regexes
            and an array of compiled checker name regexes. To be used for running certain
            checkers on certain files.
        dir_associations (arr[re.Pattern]): Stores the compiled regexes for figuring out
            which checkers to run on the entire directory.
        directory (str): The directory that the assets are contained in.
        checker_params: A dictionary containing checker parameters. Maps checker names
            to dictionaries of parameter names/values.
    """
    def __init__(self, config, directory):
        # try and load the checker modules from the directory in the loaded config
        try:
            self.checkers = sanity.module.load_checker_modules(config.checker_dir)
        except ValueError as exc:
            raise ContextCreationError(f"Could not load checker modules, {str(exc)}")
        except ImportError as exc:
            raise ContextCreationError(f"Could not load module, {str(exc)}")

        # try and load the file checker associations
        try:
            self.file_associations = sanity.associations.compile_file_associations(config.file_associations)
        except sanity.associations.AssociationError as exc:
            raise ContextCreationError(f"Could not compile file associations, {str(exc)}")

        # try to load the directory checker associations
        try:
            self.dir_associations = sanity.associations.compile_directory_associations(config.dir_associations)
        except sanity.associations.AssociationError as exc:
            raise ContextCreationError(f"Could not compile directory associations, {str(exc)}")

        self.directory = directory
        self.checker_params = config.checker_params

class ContextCreationError(Exception):
    def __init__(self, reason):
        self.reason = reason
    
    def __str__(self):
        return f"{self.reason}"

def run_check(check_func, path, checker_name, checker_params):
    result, reason = check_func(path, checker_params)
    if result is True:
        print_depth(f"[{Fore.GREEN}PASS{Style.RESET_ALL}] - {checker_name} on {path}", 1)
    else:
        print_depth(f"[{Fore.RED}FAIL{Style.RESET_ALL}] - {checker_name} on {path}, reason: {reason}", 1)
    return result

def process_checker(path, checker_regex, checkers, config_params):
    status = True
    for checker_name, checker_func in sanity.associations.filter_checkers(checkers, checker_regex):
        checker_params = config_params.get(checker_name, {})
        success = run_check(checker_func, path, checker_name, checker_params)
        
        # if at least one check failed we want to indicate this
        if not success:
            status = False
    return status
    
def process_file_association(association_name, association, files, checkers, config_params):
    print_depth(f"Processing file association: '{association_name}'")
    status = True
    for file in sanity.associations.filter_files(files, association.file_name):
        for checker_regex in association.checker_names:
            success = process_checker(file, checker_regex, checkers, config_params)

            # if at least one check failed we want to indicate this
            if not success:
                status = False
    return status

def check(context):
    # init colorama for Windows terminal color support
    colorama.init()

    # get the asset files we want to check
    files_in_dir = [f for f in listdir(context.directory) if isfile(join(context.directory, f))]

    # run the directory checks
    if len(context.dir_associations) > 0:
        print_depth(f"Processing checks for directory: {context.directory}")
        directory_check_result = True
        for dir_check_regex in context.dir_associations:
            success = process_checker(context.directory, dir_check_regex, context.checkers, context.checker_params)

            # if any check fails we want to show this
            if not success:
                directory_check_result = False
        
        if directory_check_result:
            print_depth(f"{Fore.GREEN}Directory checks PASSED!{Style.RESET_ALL}")
        else:
            print_depth(f"{Fore.RED}Directory checks FAILED.{Style.RESET_ALL}")
    
    # for all of the given file associations, run the associated checks
    file_check_result = True
    for association_name, file_association in context.file_associations.items():
        success = process_file_association(association_name, file_association, files_in_dir, 
                                           context.checkers, context.checker_params)

        if not success:
            file_check_result = False

    if file_check_result:
        print_depth(f"{Fore.GREEN}File checks PASSED!{Style.RESET_ALL}")
    else:
        print_depth(f"{Fore.RED}File checks FAILED.{Style.RESET_ALL}")
