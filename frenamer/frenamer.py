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
    "get_dir_content",
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


def get_dir_content(path: str) -> Tuple[str, List[Optional[str]], List[Optional[str]]]:
    """ارجاع محتوى المجلد

    المعطيات:
        path (str): المجلد المراد جلب محتوياته

    المخرجات:
        Tuple[str, List[Optional[str]], List[Optional[str]]]: مسار المجلد، المجلدات التي يحتويها، الملفات التي يحتويها
    """
    for root, dirs, files in os.walk(path, topdown=True):
        return (root, dirs, files)


def get_dir_name(
    start_with: str,
    root: str,
    random: Optional[bool] = False,
    length: Optional[int] = 10,
) -> str:
    """ارجاع اسم مجلد الجديد (يمكن استخدامه في المسار)

    المعطيات:
        start_with (str): بداية اسم للمجلد المراد جلبه
        root (str): المسار الذي سوف يتم وضع المجلد فيه
        random (Optional[bool], optional): تحديد ما إذا كنت تريد الاسم عشوائي ام لا. Defaults to False.
        length (Optional[int], optional): طول الاسم العشوائي اذ كنت تريد. Defaults to 10.

    المخرجات:
        str: اسم مجلد يمكن وضعه في المسار المعطى
    """
    _, dirs, _ = get_dir_content(root)
    if random:
        dir_name = "".join(choice(ascii_letters) for _ in range(length))
        while dir_name in dirs:
            dir_name = "".join(choice(ascii_letters) for _ in range(length))
        return dir_name
    else:
        for char in ascii_letters:
            dir_name = (f"{start_with}-{char}") if start_with else (char)
            if dir_name in dirs:
                continue
            else:
                return dir_name
    # يتم تشغيل هذا السطر اذ لم يجد اسم ابجدي للمجلد
    # فيتم اعاطه الاسم الاخير ولذي يكون
    # 'Z', 'Z-Z', 'Z-Z-Z' ...
    # حيث يتم تمريره كبداية للاسم
    return get_dir_name(dir_name, root, random=random, length=length)


def file_renamer(file: Path) -> dict:
    """اعادة تسمية الملف المعطى

    المعطيات:
        file (Path): الملف المراد اعادة تسميته

    المخرجات:
        dict: الاسم القديم والجديد الخاص بالملف
    """
    directory = file.parent
    _, _, files = get_dir_content(directory.as_posix())
    files = list(map(lambda file: file.split(".")[0], files))
    num = 1
    new_file_name = f"{directory.name}-{num}"
    while new_file_name in files:
        num += 1
        new_file_name = f"{directory.name}-{num}"
    new_file_name = f"{directory.name}-{num}{''.join(file.suffixes)}"
    new_path = file.rename(file.with_name(new_file_name))
    return {"old": file.name, "new": new_path.name}


def dir_renamer(
    directory: Path,
    random: Optional[bool] = False,
    length: Optional[int] = 10,
    is_root: Optional[bool] = False,
    save_data: Optional[bool] = False,
    data_filename: Optional[str] = "rename_data.json",
) -> Tuple[Path, int, int]:
    """اعادة تمسية محتوى المجلد

    المعطيات:
        directory (Path): الملجد المراد اعادة تسمية محتوياته
        random (bool): تحديد ما إذا كنت تريد اسم عشوائي للمجلد ام لا. Defaults to False.
        length (Optional[int], optional): طول الاسم العشوائي ان وجد. Defaults to 10.
        is_root (Optional[bool], optional): هل هذا المجلد الاساسي المراد تسمية محتوياته. Defaults to False.
        save_data (Optional[bool], optional): تحديد ما إذا كنت تريد حفظ الاسماء القديمة في ملف. Defaults to False.
        data_filename (Optional[str], optional): اسم الملف المراد حفظ الاسماء فيه ان وجد. Defaults to "rename_data.json".

    المخرجات:
        Tuple[Path, int, int]: المسار الجديد الخاص بالمجلد، عدد المجلدات التي تم اعادة تسميتها، عدد الملفات التي تم اعادة تسميتها
    """
    dirs_name: List[dict] = []
    files_name: List[dict] = []
    total_dirs: int = 0
    total_files: int = 0

    new_dir_name = get_dir_name(
        start_with="", root=directory.parent.as_posix(), random=random, length=length
    )
    if is_root:
        new_directory = directory
    else:
        new_directory = directory.rename(directory.with_name(new_dir_name))
        total_dirs += 1
    new_directory_path = new_directory.as_posix()
    _, dirs, files = get_dir_content(new_directory_path)

    for file in files:
        file = Path(os.path.join(new_directory_path, file))
        file_data = file_renamer(file)
        files_name.append(file_data)
        total_files += 1

    for sub_directory in dirs:
        sub_directory = Path(os.path.join(new_directory_path, sub_directory))
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
        typer.echo(f"Rename {old_name} to {new_name}")
    if save_data:
        with open(
            os.path.join(new_directory.as_posix(), data_filename),
            mode="w",
            encoding="utf-8",
        ) as f:
            obj = {
                "frenamerVersion": version,
                "names": names,
            }
            dump(obj, f, indent=4)

    return new_directory, total_dirs, total_files


def get_json_files(directory: Path, json_filename: str) -> List[Optional[str]]:
    """ارجاع جميع ملفات المطابقة لاسم ملف الجيسون في محتوى المجلد

    المعطيات:
        directory (Path): المجلد المراد استخراج منه جميع الملفات المتطايقة مع اسم ملفات الجيسون
        json_filename (str): اسم ملف الجيسون

    المخرجات:
        List[Optional[str]]: ملفات الجيسون الموجودة في المجلد
    """
    return [
        os.path.join(root, json_filename)
        for root, _, files in os.walk(directory.as_posix(), topdown=False)
        if json_filename in files
    ]


def unrename_from_json(json_file: Path, delete: bool) -> Tuple[int, int]:
    """اعادة تمسية الملفات الموجودة في ملف الجيسون

    المعطيات:
        json_file (Path): ملف الجيسون
        delete (bool): حذف ملف الجيسون بعد اعادة التسمية ام لا

    المخرجات:
        Tuple[int, int]: اجمالي المجلدات التي تم اعادة تسميتها اجمالي الملفات التي تم اعادة تسميتها
    """
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
                old_name, new_name = [
                    Path(os.path.join(path.as_posix(), name)) for name in names.values()
                ]
                new_name.rename(old_name)
                if old_name.is_dir():
                    total_dirs += 1
                else:
                    total_files += 1
                typer.echo(f"Rename {new_name.name} to {old_name.name}")
        else:
            typer.echo(
                typer.style(
                    f"Invalid frenamer format: {json_file.as_posix()}",
                    fg=typer.colors.RED,
                )
            )
    if delete:
        os.remove(json_file.as_posix())
    return total_dirs, total_files


def get_name_from_json(dir_name: str, json_file: Path) -> str:
    """جلب اسم المجلد القديم

    المعطيات:
        dir_name (str): اسم المجلد الجديد
        json_file (Path): ملف الجيسون المراد استخراج اسم المجلد القديم منه

    المخرجات:
        str: اسم المجلد القديم
    """
    names: List[dict] = loads(json_file.read_bytes()).get("names")
    return list(filter(lambda name_dct: name_dct.get("new_name") == dir_name, names))[
        0
    ].get("old_name")


def get_unrename_dir(rename_dir: Path, json_files: List[Path], root_name: str) -> str:
    """جلب المسار القديم الخاص بالمسار الجديد

    Args:
        rename_dir (Path): المسار الجديد المراد جلب مساره القديم
        json_files (List[Path]): ملفات الجيسون التي سوف يتم استخراج الاسماء القديمة منها
        root_name (str): اسم المجلد الذي يتم اعادة تسمية محتوياته

    Returns:
        str: المسار القديم
    """
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
