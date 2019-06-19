# sanity
A Python module to check the 'sanity' of assets at stages in a pipeline. Originally made for a job I applied for a while back.

## Quick start
I'd recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) to install dependencies so you don't pollute your site-packages folder. It's what I used during development.
1. `$ pip install -r requirements.txt`
2. `$ ./sanitychecker -h`
3. You're good to go! Try out some of the stuff in the usage section, and play around with making a YAML config file outlined in the config section.

## Core dependencies
- Python 3.7
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
    - `pip install pyyaml`
    - Used for loading/parsing the YAML config files.
- [colorama](https://pypi.org/project/colorama/)
    - `pip install colorama`
    - Used for making the output look pretty!

## Checker dependencies
- [PyWavefront](https://github.com/pywavefront/PyWavefront)
    - `pip install pywavefront`
    - Used for OBJ file checker

## Usage:
### General usage
```bash
$ python sanitychecker [-c CONFIG] directory
```
### Basic demo
```bash
$ python sanitychecker ./basic_demo
```
### More advanced demo
```bash
$ python sanitychecker -c extended_checkers.yml ./advanced_demo
```

## Config
Each entry here provides the name of the config value, whether or not it is required, and a short example of how it can be used.
### `checker_dir`
**(REQUIRED)** Path to the directory containing checkers. The example shown here will load all `.py` modules contained in the `~/sanity_checks` directory.
```yaml
checker_dir: "~/sanity_checks" 
```
### `file_rules`
**(OPTIONAL)** Regexes of filenames and an array of checker names to run against them. Checker names can be regexes. If this is not specified, every checker will run against every file in `checker_dir`. The example shown here will process every `.txt` file in the given directory with checkers starting with the string `"file_"`. It can be useful to separate out file and directory checkers with prefixes like this, as running file checkers on directories and vice-versa can sometimes have erroneous results.
```yaml
file_rules:
    ^.*\.txt$:
        - "^file_.*$"
```
The default value for this config processes all files with all checkers, and is equivalent to:
```yaml
file_rules:
    ^.*$:
        - "^.*$"
```
### `directory_rules`
**(OPTIONAL)** Provides a list of checker name regexes to run on the specified directory as opposed to individual files in a directory. This can be useful, as some sanity checks need to be performed on a directory - for example counting the number of files present. The following example would run all checkers prefixes with the string `"dir_"` against the directory. It can be useful to separate out file and directory checkers with prefixes like this, as running file checkers on directories and vice-versa can sometimes have erroneous results.
```yaml
directory_rules:
    - "^dir_.*$"
```
If this value isn't present then no checks will be run on the directory. It's equivalent to setting this in the config:
```yaml
directory_rules: []
```
### `parameters`
**(OPTIONAL)** Checkers can use parameterised using this value in the config. It maps variable names to values. The example shown here will set the `filename_pattern` parameter of checker '`filenamechecker.py`' to be equal to `"^.*-asset-.*$"`, indicating that it should only accept filenames that contain the string `"-asset-"`.
```yaml
parameters:
    filenamechecker:
        filename_pattern: "^.*-asset-.*$"
```
If this isn't specified then no parameters in the checkers will be set. It's equivalent to this value in the config file:
```yaml
parameters: {}
```
This means it's always recommended to provide sensible default values for any parameters used in checkers, as you don't know whether or not people will decide to not parameterise any of them.
### `recursive`
**(OPTIONAL)** If this is set to true, then the sanity checker will recurse into subdirectories of the given directory, and perform directory checks on all subdirectories, as well as file checks on all found files.
```yaml
recursive: true
```
If not specified, `recursive` defaults to `false`.

## Writing a checker
Making a checker is easy - just create a Python module with this function in it:
```python
def check(path, params):
```
Make sure it's in the folder that gets loaded when running `sanitychecker` (`checker_dir` in your config YAML file), and this checker can be called from `sanitychecker`.

It should return a 2-tuple of type `(bool, str)`, indicating True for success, False for fail, and the string contains a reason for failure. For example, if a filename was not equal to some value, you'd return `False, "file name 'name' did not equal 'desired_value'`.

For some example of checkers, please see the `./sanity/checkers` directory.

You can do almost anything with a checker. You can import other python modules/packages (as long as you don't do a relative import), and you can even call other checkers `check()` functions, which could be useful for creating some logic related to checkers being called based on the results of other checkers.

## Security concerns
**NEVER** put untrusted code in the `checker_dir` directory. Python modules in there can be executed irregardless of what the code does. There are no attempts at sandboxing the way these modules are executed, and theoretically they could perform any number of malicious actions on the host machine.

## Future work
- Different parameters could be used for checkers based on which file/directory rule is currently in use?
- Load checkers from a list of different directories.