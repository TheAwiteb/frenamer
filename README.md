<div align="center">
  <h1>Frenamer (file-renamer)</h1>
  <img alt="Frenamer-logo" src="https://i.suar.me/Gxlly/s"><br>
  <p>Rename and unrename all files in the directory, alphabetically or randomly</p>
  <a href="https://pypi.org/project/frenamer/">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/frenamer?color=9cf">
  </a>
  <a href="https://pypi.org/project/frenamer/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/frenamer?color=9cf">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/pypi/l/frenamer?color=9cf&label=License" alt="License">
  </a>
  <br>
    <a href="https://github.com/TheAwiteb/frenamer/actions/workflows/python-app.yml">
    <img alt="test-frenamer" src="https://github.com/TheAwiteb/frenamer/actions/workflows/python-app.yml/badge.svg">
  </a>
  <a href="https://github.com/TheAwiteb/frenamer/actions/workflows/release.yml">
    <img alt="Upload Python Package" src="https://github.com/TheAwiteb/frenamer/actions/workflows/release.yml/badge.svg">
  </a>
  <br>
  <a href="https://github.com/psf/black">
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
  </a>
</div>

<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#Requirements">Requirements</a>
    </li>
    <li>
      <a href="#Installation">Installation</a>
      <ul>
        <li><a href="#PyPi">With PyPi</a></li>
        <li><a href="#GitHub">With GitHub</a></li>
        <li><a href="#Update">Update</a></li>
      </ul>
    </li>
    <li>
        <a href="#Usage">Usage</a>
        <ul>
            <li><a href="#Help-message">Help message</a></li>
            <li>
                <a href="#Rename">Rename</a>
                <ul>
                    <li><a href="#Help-message">Help message</a></li>
                    <li><a href="#Alphabetically">Alphabetically</a></li>
                    <li><a href="#Randomly">Randomly</a></li>
                </ul>
            </li>
            <li>
                <a href="#Unrename">Unrename</a>
                <ul>
                    <li><a href="#Help-message">Help message</a></li>
                </ul>
            </li>
        </ul>
    </li>
    <li><a href="#Discussions">Discussions</a></li>
    <li><a href="#Issues">Issues</a></li>
    <li><a href="#License">License</a></li>
  </ol>
</details>


## Requirements

* [Python](https://Python.org/) >= 3.8

## Installation

### PyPi

```bash
$ pip3 install frenamer
```

### GitHub

```bash
$ git clone https://github.com/TheAwiteb/frenamer/
$ cd frenamer
$ sudo python3 setup.py install
```

### Update
```bash
$ python3 -m pip install frenamer --upgrade
```

## Note
> if `frenamer --help` don't work with you use `python3 -m frenamer --help` or `py -m frenamer --help` for windows

## Usage

### Help message

```
Usage: frenamer [OPTIONS] COMMAND [ARGS]...

  Frenamer (File-Renamer) Tool help you to rename files and directories
  alphabetical or random names

Options:
  -V, --version  Frenamer (File-Renamer) version.
  --help         Show this message and exit.

Commands:
  rename    Rename directories with random names or alphabetical order.
  unrename  unrename directories, fetching old names from json files.
```

### Rename

#### Help message
```
Usage: frenamer rename [OPTIONS] DIRECTORIES...

  Rename directories with random names or alphabetical order.

Arguments:
  DIRECTORIES...  Directories whose contents you want to rename.  [required]

Options:
  -r, --random          Rename with random names, or alphabetically.
  -l, --length INTEGER  Random name length.  [default: 10]
  -s, --save-date       Save directory names before and after renaming.
  -f, --filename TEXT   The name of the json file in which the directory names
                        are to be saved.  [default: rename_data.json]
  --help                Show this message and exit.

```

#### Alphabetically

```bash
$ frenamer rename <my_directory>
$ frenamer rename --save-date  <my_directory>
$ frenamer rename --save-date --filename data.json <my_directory>
```

#### Randomly

```bash
$ frenamer rename --random <my_directory>
$ frenamer rename --random --length 15  <my_directory>
```

### Unrename

#### Help message
```
Usage: frenamer unrename [OPTIONS] DIRECTORIES...

  unrename directories, fetching old names from json files.

Arguments:
  DIRECTORIES...  Directories whose contents you want to unrename.  [required]

Options:
  -d, --delete         Delete the JSON files that were used in the unrenaming
                       after completion.
  -f, --filename TEXT  The name of the json file from which the directory
                       names will be extracted.  [default: rename_data.json]
  --help               Show this message and exit.

```

```bash
$ frenamer unrename <my_directory>
$ frenamer unrename --filename data.json <my_directory>
$ frenamer unrename --delete <my_directory>
```

## Discussions
Question, feature request, discuss about frenamer [here](https://github.com/TheAwiteb/frenamer/discussions)

## Issues
You can report a bug [here](https://github.com/TheAwiteb/frenamer/issues)

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.