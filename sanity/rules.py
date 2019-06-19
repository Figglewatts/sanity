"""Defines functions and classes related to compiling and applying rules loaded
in from the config file.

For more info on how to make rules, please refer to the README.

Author:
    Sam Gibson <samolivergibson@gmail.com>
"""

import re

class FileCheckerRule:
    """Stores a compiled filename matcher regular expression and an array of
    checker name matcher regular expressions, intended to be executed when
    checking the asset files individually in the directory.

    Args:
        file_name (re.Pattern): The compiled filename regex.
        checker_names (list[re.Pattern]): The compiled checker name regexes.

    Attributes:
        See Args.
    """
    def __init__(self, file_name, checker_names):
        self.file_name = file_name
        self.checker_names = checker_names

class RuleError(Exception):
    """Raised when there was some error compiling a rule."""
    def __init__(self, message, rule_name):
        self.message = message
        self.rule_name = rule_name

    def __str__(self):
        return f"Bad rule '{self.rule_name}', {self.message}"

def compile_rule_re(regex, rule_name):
    """Try compiling a rule's regex expression.

    Args:
        regex (str): The regex to compile.
        rule_name (str): The name of the rule. Used to display helpful error info.

    Raises:
        RuleError: If the rule could not be compiled.

    Returns:
        re.Pattern: The compiled rule.
    """
    try:
        return re.compile(regex)
    except re.error as exc:
        raise RuleError(f"Could not compile regex {regex}, {str(exc)}", rule_name)

def compile_file_rules(file_rules):
    """From the parsed file_rules from the config file, compile all of the rules.

    Args:
        file_rules (dict): Parsed from the config file.

    Raises:
        RuleError: If there was an error compiling any of the rules.

    Returns:
        dict: The compiled rules.
    """
    compiled_rules = {}
    # for each rule, go through and compile each one
    for file_match_re, checker_name_re_arr in file_rules.items():
        # compile the filename match rule
        compiled_file_match = compile_rule_re(file_match_re, file_match_re)

        # now go through and compile all of the given checker name rules
        compiled_checker_name_matchers = []
        for checker_name_re in checker_name_re_arr:
            compiled_checker_name_matchers.append(compile_rule_re(checker_name_re, file_match_re))
        compiled_rules[file_match_re] = FileCheckerRule(compiled_file_match, compiled_checker_name_matchers)
    return compiled_rules

def compile_directory_rules(dir_rules):
    """From the parsed dir_rules from the config file, compile all of the rules.

    Args:
        dir_rules (list): Parsed from the config file.

    Raises:
        RuleError: If there was an error compiling any of the rules.

    Returns:
        list: The compiled rules.
    """
    compiled_rules = []
    for dir_check_re in dir_rules:
        compiled_dir_check = compile_rule_re(dir_check_re, dir_check_re)
        compiled_rules.append(compiled_dir_check)
    return compiled_rules

def filter_files(files, filter_rule):
    """For a given list of files and a compiled regex to match filenames,
    yield only the files that match.

    Args:
        files (arr[str]): A list containing all files to filter.
        filter_rule (re.Pattern): A regex to match filenames against.

    Yields:
        str: Filenames of matching files.
    """
    for file in files:
        if filter_rule.match(file):
            yield file

def filter_checkers(checkers, filter_rule):
    """For a given list of checkers and a compiled regex to match checker names,
    yield only the checkers that match.

    Args:
        checkers (dict[str, func]): A map of checker names to loaded check() functions.
        filter_rule (re.Pattern): A regex to match filenames against.

    Yields:
        (str, func): The checker name and check() function of matching checkers.
    """
    for checker_name, checker_func in checkers.items():
        if filter_rule.match(checker_name):
            yield checker_name, checker_func