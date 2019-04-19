import re

class Association:
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

def compile_associations(associations):
    compiled_associations = {}
    for association in associations:
        for file_match_re, checker_name_res in association.items():
            compiled_file_match = compile_association_re(file_match_re, file_match_re)
            compiled_checker_name_matchers = []
            for checker_name_re in checker_name_res:
                compiled_checker_name_matchers.append(compile_association_re(checker_name_re, file_match_re))
            compiled_associations[file_match_re] = Association(compiled_file_match, compiled_checker_name_matchers)
    return compiled_associations

def filter_files(files, filter_regex):
    for file in files:
        if filter_regex.match(file):
            yield file

def filter_checkers(checkers, checker_regex):
    for checker_name, checker_func in checkers.items():
        if checker_regex.match(checker_name):
            yield checker_name, checker_func