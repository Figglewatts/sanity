import re

class FileCheckerAssociation:
    """Stores a compiled filename matcher regular expression and an array of
    checker name matcher regular expressions, intended to be executed when
    checking the asset files individually in the directory.

    Args:
        file_name (re.Pattern): The compiled filename regex.
        checker_names (arr[re.Pattern]): The compiled checker name regexes.

    Attributes:
        See Args.
    """
    def __init__(self, file_name, checker_names):
        self.file_name = file_name
        self.checker_names = checker_names

class AssociationError(Exception):
    def __init__(self, message, association_name):
        self.message = message
        self.association_name = association_name

    def __str__(self):
        return f"Bad association '{self.association_name}', {self.message}"

def compile_association_re(regex, association_name):
    try:
        return re.compile(regex)
    except re.error as exc:
        raise AssociationError(f"Could not compile regex {regex}, {str(exc)}", association_name)

def compile_file_associations(file_associations):
    compiled_associations = {}
    for file_match_re, checker_name_re_arr in file_associations.items():
        compiled_file_match = compile_association_re(file_match_re, file_match_re)
        compiled_checker_name_matchers = []
        for checker_name_re in checker_name_re_arr:
            compiled_checker_name_matchers.append(compile_association_re(checker_name_re, file_match_re))
        compiled_associations[file_match_re] = FileCheckerAssociation(compiled_file_match, compiled_checker_name_matchers)
    return compiled_associations

def compile_directory_associations(dir_associations):
    compiled_associations = []
    for dir_check_re in dir_associations:
        compiled_dir_check = compile_association_re(dir_check_re, dir_check_re)
        compiled_associations.append(compiled_dir_check)
    return compiled_associations

def filter_files(files, filter_regex):
    for file in files:
        if filter_regex.match(file):
            yield file

def filter_checkers(checkers, checker_regex):
    for checker_name, checker_func in checkers.items():
        if checker_regex.match(checker_name):
            yield checker_name, checker_func