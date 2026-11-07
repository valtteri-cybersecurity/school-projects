from app.cli.ui import clear_screen, print_line, print_empty_line

def print_error(message: str) -> None:
    print(f"Error: {message}")

def print_success(message: str) -> None:
    print(f"Success: {message}")

def print_info(message: str) -> None:
    print(f"Info: {message}")

def print_valid_number() -> None:
    print("Please type valid number!")

def print_dirname_cant_be_empty() -> None:
    print("Directory name cant be empty!")

def print_dirname_cant_contain_spaces() -> None:
    print("Directory name cant contain spaces!")

def print_dirname_cant_start_number() -> None:
    print("Directory name cant start by number!")

def print_dirname_cant_contain_special_char() -> None:
    print("Directory name can't contain special characters!")

def print_ask_saving_location():
    print_line()
    print_empty_line(1)
    print("Give name of the directory where you want to create new directory.")
    print("To quit type 0.")
    print_empty_line(1)
    print_line()

def ask_newdir_name_questions() -> None:
    print("Give name of the new directory.")
    print("To quit type 0.")

def ask_continue_question() -> None:
    print("Continue?")
    print("Answer 1 to continue")

def print_directory_list(directory_dict) -> None:
    clear_screen()
    print_line()
    print_empty_line(1)
    directories = directory_dict

    for key, value in directories.items():
        print(f"{key}:   {value}")

def print_new_dir_created(newdir_name):
    print_info(f"New directory: {newdir_name} has been created!")

def print_ask_target_directory():
    print("Choose number of directory to enter")
    print("0 = Parent directory")
    print("q = Return to main menu")

def print_directory_navigation_menu():
    print_empty_line(1)
    print_line()
    print_empty_line(1)
    print_ask_target_directory()
    print_empty_line(1)
    print_line()
    print_empty_line(1)

def print_program_shutting_down():
    print_info("Program shutting down...")

