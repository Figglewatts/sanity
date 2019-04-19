# sanity
A Python module to check the 'sanity' of assets at stages in a pipeline.

## Quick start
I'd recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) to install dependencies so you don't pollute your site-packages folder. It's what I used during development.
1. `$ pip install -r requirements.txt`
2. `$ ./sanitychecker -h`
3. You're good to go! Try out some of the stuff in the usage section, and play around with making a YAML config file outlined in the config section.

## Dependencies
- Python 3.7
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
    - `pip install pyyaml`

## Check ideas
- Check regex filename
- Check regex directory name
- Check if directory is empty (dir)
- Check if directory has certain file count (dir)
- Check if files in directory are certain size
- Check if files exist

## Usage:
```bash
$ python sanitychecker [-c CONFIG] directory
```

## Config
- `checker_dir`: Path to the directory containing checkers. (REQUIRED)
- `file_checker_associations`: Regexes of filenames and an array of checker names to run against them. Checker names can be regexes. If this is not specified, every checker will run against every file in `checker_dir`.

## Todo
- Make more file rules to demo
- Directory rules for processing files in a directory
- Refactor out functionality from sanitychecker to sanity.checker
- Make it really reusable
- Parameterise variables in checkers?
    - For example a file size limit checker could have the max file size set in the YAML config
- Create an alternate config to demo utility of other configs
- Create advanced checkers, like an OBJ loader or something... (vertex count?)
    - JSON checker (JSON schema?)
    - YAML checker
    - XML checker
    - PE, ELF, Mach-O?
    - Markdown
    - GLSL/HLSL
    - Pylint
    - Texture dimensions
- Recursive check (configurable in config)
- Checks should return a reason for failing
- Ability to combine checks into one check (like combining unit test cases)
- Write documentation for everything
- Update the README to be a guide how to use