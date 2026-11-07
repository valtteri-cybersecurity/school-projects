import os

from app.services.directory_service import verify_dir_name, dir_exists
from app.cli.output import print_error, print_info, print_ask_saving_location, ask_newdir_name_questions, print_valid_number, print_directory_navigation_menu
from app.cli.ui import print_line, clear_screen, wait_user_read, print_empty_line

def three_option_navigation() -> int:
    while True:
        try:
            choice = int(input("Choose action 1, 2 or to quit type 0: "))

            if not choice in [1,2,0]:
                print_valid_number()
                continue
            else:
                if choice == 0:
                    return None
                else:
                    return choice
        except ValueError:
            print_valid_number()
            continue


def ask_saving_location() -> str | None:
    while True:
        clear_screen()
        print_line()
        print_ask_saving_location()
        print_line()

        base_dir = input("Your choice: ")
        
        if base_dir == "0":
            return None
        
        elif verify_dir_name(base_dir):
            home = os.path.expanduser("~")
            base_dir_path = os.path.join(home, base_dir)
            if dir_exists(base_dir_path):
                
                print_empty_line(1)
                print_info("Found your directory!")
                print_empty_line(1)

                wait_user_read()
                return base_dir_path
            else:
                print_error(f"Directory: {base_dir_path} does not exist")

                print_empty_line(1)
                wait_user_read()
                continue
        else:
            continue


def ask_newdir_name(base_dir_path: str) -> str | None:
    while True:
        clear_screen()

        print_line()
        print_empty_line(1)
        ask_newdir_name_questions()
        print_empty_line(1)
        print_line()
        
        dir_name = input("Your choice: ")

        if dir_name == "0":
            return None
        elif verify_dir_name(dir_name):
            abs_path = os.path.join(base_dir_path, dir_name)
            return abs_path
        else:
            continue



def ask_dir_from_list(directory_dict: dict, dictionary_len: int) -> int | None:
    while True:
        try:
            print_directory_navigation_menu()

            user_input = input("Your choice: ")

            if user_input.lower() == "q":
                return None

            choice = int(user_input)

            if choice == 0:
                return 0

            if choice in directory_dict:
                return choice

            print_valid_number()

        except ValueError:
            print_valid_number()

