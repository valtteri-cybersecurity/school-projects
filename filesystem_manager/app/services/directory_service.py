import os
from pathlib import Path

from app.cli.output import print_dirname_cant_be_empty, print_dirname_cant_contain_spaces, print_dirname_cant_start_number, print_dirname_cant_contain_special_char


def verify_dir_name(name: str) -> bool:
    if name == "":
        print_dirname_cant_be_empty()
        return False
    elif " " in name:
        print_dirname_cant_contain_spaces()
        return False
    elif name[0].isdigit():
        print_dirname_cant_start_number()
        return False
    elif not name.replace("_", "").replace("-", "").isalnum():
        print_dirname_cant_contain_special_char()
        return False
    else:
        return True


def dir_exists(path: str) -> bool:
    return os.path.isdir(path)


def create_new_dir(newdir_name: str) -> None:
    os.mkdir(newdir_name)


def create_home_path() -> Path:
    return Path.home()    


def list_directory(directory: Path) -> dict[int, Path]:
    folders = []

    for item in directory.iterdir():
        if item.is_dir() and not item.is_symlink():
            folders.append(item)

    folders.sort(key=lambda item: item.name.casefold())

    result = {}

    for index, folder in enumerate(folders, start=1):
        result[index] = folder

    return result


def count_dir_len(directory_dict: dict) -> int:
    return len(directory_dict)


def navigate_in_filesystem(home_directory_dict, user_target_dir):
    return home_directory_dict[user_target_dir]