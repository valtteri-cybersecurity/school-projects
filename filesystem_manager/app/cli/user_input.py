import os

from app.services.directory_service import verify_dir_name, dir_exists
from app.cli.output import print_error

def ask_creation_mode() -> int:
    while True:
        try:
            choice = int(input("Create new directory(1) or Create many directories(2) or type(0) to quit: "))
            if choice not in [0,1,2]:
                message = "Choose 0, 1 or 2"
                print_error(message)
                continue
        except ValueError:
            message = "Only numbers allowed!"
            print_error(message)
            continue

        return choice


def ask_saving_location() -> str | None:
    while True:
        base_dir = input("Give name of the directory where you want to create new directory or type(0) to quit: ")

        if base_dir == "0":
            return None
        
        if verify_dir_name(base_dir):
            home = os.path.expanduser("~")
            base_dir_path = os.path.join(home, base_dir)
            if dir_exists(base_dir_path):
                return base_dir_path
            else:
                message = f"Directory: {base_dir_path} does not exist"
                print_error(message)
                continue
        else:
            continue


def ask_newdir_name(base_dir_path: str) -> str | None:
    while True:
        dir_name = input("Give name of the directory to create or type(0) to quit: ")

        if dir_name == "0":
            return None
        if verify_dir_name(dir_name):
            abs_path = os.path.join(base_dir_path, dir_name)
            return abs_path
        else:
            continue


