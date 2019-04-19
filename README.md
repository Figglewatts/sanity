# sanity
A Python module to check the 'sanity' of assets at stages in a pipeline.

## Quick start
1. `$ pip install -r requirements.txt`

## Dependencies
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
$ python sanity.py [config] [directory]
```