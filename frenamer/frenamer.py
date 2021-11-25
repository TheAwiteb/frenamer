import os
from time import time
import typer
from json import dump, load, loads
from pathlib import Path
from typing import List, Tuple, Optional
from random import choice
from string import ascii_letters

if __name__ != "__main__":
    from .version import version

home_help_message = """
Usage: python3 -m frenamer [OPTIONS] COMMAND [ARGS]...

    Frenamer (File-Renamer) Tool help you to rename files and directories
    alphabetical or random names.

Options:
    -V, --version  Frenamer (File-Renamer) version.
    -h, --help     Show this message and exit.

Commands:
    rename    rename directories.
    unrename  unrename directories.
"""

rename_help_message = """
Usage: python3 -m frenamer rename [OPTIONS] DIRECTORIES...

    rename directories.

    Arguments:
    DIRECTORIES...  Directories whose contents you want to rename.  [required]

    Options:
    -r, --random                Rename with random names, or alphabetically.
                                [default: False]

    -l, --length INTEGER        Random name length.  [default: 10]
    -s, --save-date             Save directory names before and after renaming.
                                [default: False]

    -f, --filename TEXT         The name of the json file in which the directory
                                names are to be saved.  [default:
                                rename_data.json]

    -h, --help                   Show this message and exit.
"""

unrename_help_message = """
Usage: python3 -m frenamer unrename [OPTIONS] DIRECTORIES...

    unrename directories.

    Arguments:
    DIRECTORIES...  Directories whose contents you want to unrename.  [required]

    Options:
    -d, --delete         Delete the JSON files that were used in the unrenaming
                        after completion.  [default: False]

    -f, --filename TEXT  The name of the json file from which the directory
                        names will be extracted.  [default: rename_data.json]


    -h, --help            Show this message and exit.
"""

app = typer.Typer(
    name="Frenamer",
    help="Frenamer (File-Renamer)\nTool help you to rename files and directories alphabetical or random names",
    add_completion=False,
)

__all__ = (
    "app",
    "get_content",
    "get_dir_name",
    "file_renamer",
    "dir_renamer",
    "get_json_files",
    "unrename_from_json",
    "get_unrename_dir",
    "get_name_from_json",
    "get_unrename_dir",
    "rename",
    "unrename",
)


def get_content(path: str) -> Tuple[str, List[Optional[str]], List[Optional[str]]]:
    for root, dirs, files in os.walk(path, topdown=True):
        return (root, dirs, files)


def get_dir_name(start_with: str, root: str, random: bool, length: int) -> str:
    _, dirs, _ = get_content(root)
    if random:
        dir_name = "".join(choice(ascii_letters) for _ in range(length or 10))
        while dir_name in dirs:
            dir_name = "".join(choice(ascii_letters) for _ in range(length or 10))
        return dir_name
    else:
        for char in ascii_letters:
            dir_name = (f"{start_with}-{char}") if start_with else char
            if dir_name in dirs:
                continue
            else:
                return dir_name
    return get_dir_name(dir_name, root, random=random, length=length)


def file_renamer(path: Path, dir_name: str) -> dict:
    _, _, files = get_content(path.parent.as_posix())
    files = list(map(lambda file: file.split(".")[0], files))
    num = 1
    new_file_name = f"{dir_name}-{num}"
    while new_file_name in files:
        num += 1
        new_file_name = f"{dir_name}-{num}"
    new_file_name = f"{dir_name}-{num}{''.join(path.suffixes)}"
    new_path = path.rename(path.with_name(new_file_name))
    return {"old": path.name, "new": new_path.name}


def dir_renamer(
    directory: Path,
    random: bool,
    length: Optional[int] = None,
    is_root: Optional[bool] = False,
    save_data: Optional[bool] = None,
    data_filename: Optional[str] = "rename_data.json",
) -> Tuple[Path, int, int]:
    dirs_name: List[dict] = []
    files_name: List[dict] = []
    total_dirs: int = 0
    total_files: int = 0

    new_dir_name = get_dir_name(
        "", root=f"{directory.as_posix()}/..", random=random, length=length
    )
    if is_root:
        new_directory = directory
    else:
        new_directory = directory.rename(directory.with_name(new_dir_name))
        total_dirs += 1
    new_directory_path = new_directory.as_posix()
    _, dirs, files = get_content(new_directory_path)

    for file in files:
        file = Path(f"{new_directory_path}/{file}")
        file_data = file_renamer(file, new_directory.name)
        files_name.append(file_data)
        total_files += 1

    for sub_directory in dirs:
        sub_directory = Path(f"{new_directory_path}/{sub_directory}")
        new_sub_directory, total_dirs_, total_files_ = dir_renamer(
            sub_directory,
            random=random,
            length=length,
            save_data=save_data,
            data_filename=data_filename,
        )
        total_dirs += total_dirs_
        total_files += total_files_
        dirs_name.append(
            {"old_name": sub_directory.name, "new_name": new_sub_directory.name}
        )

    names = dirs_name + files_name
    typer.echo(
        typer.style(
            "Directory: " + new_directory.as_posix(),
            fg=typer.colors.CYAN,
        )
    )

    for file in names:
        old_name, new_name = file.values()
        old_name = typer.style(
            old_name,
            fg=(
                typer.colors.MAGENTA if os.path.isfile(os.path.join(new_directory.as_posix(), old_name)) else typer.colors.BRIGHT_MAGENTA
            ),
        )
        new_name = typer.style(
            new_name,
            fg=(
                typer.colors.MAGENTA if os.path.isfile(os.path.join(new_directory.as_posix(), new_name)) else typer.colors.BRIGHT_MAGENTA
            ),
        )
        typer.echo(f"Rename {old_name} to {new_name}")
    if save_data:
        with open(
            f"{new_directory.as_posix()}/{data_filename}", mode="w", encoding="utf-8"
        ) as f:
            obj = {
                "frenamerVersion": version,
                "names": names,
            }
            dump(obj, f, indent=4)

    return new_directory, total_dirs, total_files


def get_json_files(directory: Path, json_filename: str) -> List[str]:
    return [
        f"{root}/{json_filename}"
        for root, _, files in os.walk(directory.as_posix(), topdown=False)
        if json_filename in files
    ]


def unrename_from_json(json_file: Path, delete: bool) -> Tuple[int, int]:
    total_dirs = 0
    total_files = 0
    path = json_file.parent
    with open(json_file, "r") as f:
        rename_data = load(f)
        if "frenamerVersion" in rename_data and "names" in rename_data:
            if rename_data.get("frenamerVersion") != version:
                typer.echo(
                    typer.style(
                        f"Warning The current frenamer version ({version}) does not match the frenamer version ({rename_data.get('frenamerVersion')}) in which the files were renamed: {json_file.as_posix()}",
                        fg=typer.colors.YELLOW,
                    )
                )
            for names in rename_data.get("names"):
                old_name, new_name = [Path(f"{path}/{name}") for name in names.values()]
                new_name.rename(old_name)
                if old_name.is_dir():
                    total_dirs += 1
                else:
                    total_files += 1
                old_name = typer.style(
                    old_name.name,
                    fg=(
                        typer.colors.MAGENTA
                        if os.path.isfile(os.path.join(old_name.as_posix()))
                        else typer.colors.BRIGHT_MAGENTA
                    ),
                )
                new_name = typer.style(
                    new_name.name,
                    fg=(
                        typer.colors.MAGENTA
                        if os.path.isfile(os.path.join(new_name.as_posix()))
                        else typer.colors.BRIGHT_MAGENTA
                    ),
                )
                typer.echo(f"Rename {new_name} to {old_name}")
        else:
            typer.echo(
                typer.style(
                    f"Invalid frenamer format: {json_file.as_posix()}",
                    fg=typer.colors.RED,
                )
            )
    if delete:
        os.remove(json_file)
    return total_dirs, total_files


def get_name_from_json(dir_name: str, json_file: Path) -> str:
    names: List[dict] = loads(json_file.read_bytes()).get("names")
    return list(filter(lambda name_dct: name_dct.get("new_name") == dir_name, names))[
        0
    ].get("old_name")


def get_unrename_dir(rename_dir: Path, json_files: List[Path], root_name: str) -> str:
    paths: List[Path] = list(
        map(
            lambda json_file: (
                json_file.parent,
                json_file.parent.with_name(json_file.name),
            ),
            json_files,
        )
    )
    unrename_dir = ""
    current_path = ""
    for part in rename_dir.parts:
        part_ = part
        if part != root_name:
            path = os.path.join(current_path, part)
            if path in list(map(lambda tup: tup[0].as_posix(), paths)):
                part_ = get_name_from_json(
                    part,
                    list(filter(lambda tup: tup[0].as_posix() == path, paths))[0][1],
                )
        unrename_dir = os.path.join(unrename_dir, part_)
        current_path = os.path.join(current_path, part)
    return unrename_dir


def version_callback(value: bool) -> None:
    """
    -V, --version option callback
    """
    if value:
        typer.echo(f"Frenamer (File-Renamer) CLI Version: {version}")
        raise typer.Exit()


def home_help_callback(value: bool) -> None:
    """
    -h, --help option callback
    """
    if value:
        typer.echo(home_help_message)
        raise typer.Exit()


def rename_help_callback(value: bool) -> None:
    """
    -h, --help option callback
    """
    if value:
        typer.echo(rename_help_message)
        raise typer.Exit()


def unrename_help_callback(value: bool) -> None:
    """
    -h, --help option callback
    """
    if value:
        typer.echo(unrename_help_message)
        raise typer.Exit()


@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        False,
        "--version",
        "-V",
        help="Frenamer (File-Renamer) version.",
        callback=version_callback,
        show_default=False,
    ),
    help: Optional[bool] = typer.Option(
        False,
        "--help",
        "-h",
        help="Show this message and exit.",
        callback=home_help_callback,
        is_eager=True,
        show_default=False,
    ),
) -> None:
    pass


@app.command()
def rename(
    directories: List[Path] = typer.Argument(
        ...,
        help="Directories whose contents you want to rename.",
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
    ),
    random: Optional[bool] = typer.Option(
        False, "--random", "-r", help="Rename with random names, or alphabetically."
    ),
    length: Optional[int] = typer.Option(
        10, "--length", "-l", help="Random name length."
    ),
    save_rename_data: Optional[bool] = typer.Option(
        False,
        "--save-date",
        "-s",
        help="Save directory names before and after renaming.",
    ),
    rename_data_filename: Optional[str] = typer.Option(
        "rename_data.json",
        "--filename",
        "-f",
        help="The name of the json file in which the directory names are to be saved.",
    ),
    help: Optional[bool] = typer.Option(
        False,
        "--help",
        "-h",
        help="Show this message and exit.",
        callback=rename_help_callback,
        is_eager=True,
        show_default=False,
    ),
) -> None:
    """
    rename directories.
    """
    start_time = time()
    total_dirs: int = 0
    total_files: int = 0
    rename_data_filename = f"{rename_data_filename.split('.')[0]}.json"
    for directory in directories:
        _, total_dirs_, total_files_ = dir_renamer(
            directory,
            random=random,
            length=length,
            is_root=True,
            save_data=save_rename_data,
            data_filename=rename_data_filename,
        )
        total_dirs += total_dirs_
        total_files += total_files_

    total_dirs = typer.style(str(total_dirs), fg=typer.colors.BRIGHT_MAGENTA)
    total_files = typer.style(str(total_files), fg=typer.colors.MAGENTA)

    typer.echo(
        f"\nRenaming {total_dirs} directories, {total_files} files, in {round(time() - start_time, 4)}"
    )

    typer.echo(
        f"The name of the file containing the rename data is {typer.style(rename_data_filename, fg=typer.colors.BLUE)}"
        if save_rename_data
        else ""
    )


@app.command(name="unrename")
def unrename(
    directories: List[Path] = typer.Argument(
        ...,
        help="Directories whose contents you want to unrename.",
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
    ),
    delete_json_files: Optional[bool] = typer.Option(
        False,
        "--delete",
        "-d",
        help="Delete the JSON files that were used in the unrenaming after completion.",
    ),
    json_filename: Optional[str] = typer.Option(
        "rename_data.json",
        "--filename",
        "-f",
        help="The name of the json file from which the directory names will be extracted.",
    ),
    help: Optional[bool] = typer.Option(
        False,
        "--help",
        "-h",
        help="Show this message and exit.",
        callback=unrename_help_callback,
        is_eager=True,
        show_default=False,
    ),
) -> None:
    """
    unrename directories.
    """
    start_time = time()
    total_dirs: int = 0
    total_files: int = 0
    json_filename = f"{json_filename.split('.')[0]}.json"
    for directory in directories:
        json_files: List[Path] = list(
            map(Path, get_json_files(directory=directory, json_filename=json_filename))
        )
        if len(json_files) >= 1:
            for json_file in json_files:
                typer.echo(
                    typer.style(
                        "Directory: "
                        + get_unrename_dir(
                            json_file.parent, json_files, root_name=directory.name
                        ),
                        fg=typer.colors.CYAN,
                    )
                )
                total_dirs_, total_files_ = unrename_from_json(
                    json_file=json_file, delete=delete_json_files
                )
                total_dirs += total_dirs_
                total_files += total_files_
        else:
            typer.echo(
                typer.style(
                    f"There is no JSON file named {json_filename} in this directory {directory.as_posix()}",
                    fg=typer.colors.RED,
                )
            )
    total_dirs = typer.style(str(total_dirs), fg=typer.colors.BRIGHT_MAGENTA)
    total_files = typer.style(str(total_files), fg=typer.colors.MAGENTA)
    typer.echo(
        f"\nRenaming {total_dirs} directories, {total_files} files, in {round(time() - start_time, 4)}"
    )


if __name__ == "__main__":

    typer.echo(
        typer.style("Try again, the correct way to run the tool is ", fg="red")
        + "'python3 -m frenamer -h'"
    )
