# sanity
A Python module to check the 'sanity' of assets at stages in a pipeline.

## Quick start
1. `$ pip install -r requirements.txt`
2. `$ ./sanitychecker -h`

## Dependencies
- Python 3.7
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
    - `pip install pyyaml`

## Check ideas
- Check regex filename
- Check regex directory name
- Check if directory is empty
- Check if directory has certain file count
- Check if files in directory are certain size
- Check if files exist
- 

## Usage:
```bash
$ python sanitychecker [-c CONFIG] directory
```

## Config
- `checker_dir`: Path to the directory containing checkers. (REQUIRED)
- `file_checker_associations`: Regexes of filenames and an array of checker names to run against them. Checker names can be regexes. If this is not specified, every checker will run against every file in `checker_dir`.