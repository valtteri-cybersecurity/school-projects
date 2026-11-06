import os

from app.cli.output import print_error
def verify_dir_name(name: str) -> bool:
    if name == "":
        message = "Directory name cant be empty"
        print_error(message)
        return False
    elif " " in name:
        message = "Directory name cant contain spaces!"
        print_error(message)
        return False
    elif name[0].isdigit():
        message = "Directory name cant start by number!"
        print_error(message)
        return False
    elif not name.replace("_", "").replace("-", "").isalnum():
        message = "Directory name can't contain special characters!"
        print_error(message)
        return False
    else:
        return True

def dir_exists(path: str) -> bool:
    return os.path.isdir(path)

def create_new_dir(newdir_name: str) -> None:
    os.mkdir(newdir_name)


