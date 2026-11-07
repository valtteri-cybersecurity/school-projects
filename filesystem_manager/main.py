from app.cli.user_input import (
    ask_saving_location,
    ask_newdir_name,
    three_option_navigation,
    ask_dir_from_list
)
from app.services.directory_service import create_new_dir, create_home_path, list_directory, count_dir_len, navigate_in_filesystem
from app.cli.menu import (
    print_menu,
    print_create_menu,
    print_create_dirs_menu,
    print_show_menu,
    print_multiple_dirs_menu,
)
from app.cli.output import print_directory_list, print_new_dir_created, print_program_shutting_down

def main() -> None:
    current_directory = create_home_path()
####################################################################################
#MAIN-MENU
    while True:

        print_menu()
        menu_nav = three_option_navigation()

        if menu_nav == None:
            print_program_shutting_down()
            break

        if menu_nav == 1:

#CREATE-MENU
            while True:
                print_create_menu()
                create_menu_nav = three_option_navigation()

                if create_menu_nav == None:
                    break

                if create_menu_nav == 1:

#CREATE_DIR_MENU
                    while True:
                        print_create_dirs_menu()
                        creation_mode = three_option_navigation()

                        if creation_mode == None:
                            break

                        if creation_mode == 1:

#ASK_SAVING_LOCATION - clear_screen is used in ask_saving_location-function
                            while True:
                                location = ask_saving_location()

                                if location is None:
                                    break

                                newdir_name = ask_newdir_name(location)

                                if newdir_name is None:
                                    continue

                                create_new_dir(newdir_name)
                                print_new_dir_created(newdir_name)
                                input("Press Enter to continue...")
                                break

#CREATE_MULTIPLE_DIRECTORIES
                        elif creation_mode == 2:
                            while True:
                                print_multiple_dirs_menu()
                                multiple_mode = three_option_navigation()

                                if multiple_mode is None:
                                    break

                                if multiple_mode == 1:
                                    location = ask_saving_location()

                                    if location is None:
                                        continue

                                    while True:
                                        newdir_name = ask_newdir_name(location)

                                        if newdir_name is None:
                                            break

                                        create_new_dir(newdir_name)
                                        print_new_dir_created(newdir_name)
                                        input("Press Enter to continue...")

                                elif multiple_mode == 2:
                                    while True:
                                        location = ask_saving_location()

                                        if location is None:
                                            break

                                        newdir_name = ask_newdir_name(location)

                                        if newdir_name is None:
                                            continue

                                        create_new_dir(newdir_name)
                                        print_new_dir_created(newdir_name)
                                        input("Press Enter to continue...")

#LIST_DIRECTORIES
        elif menu_nav == 2:
            print_show_menu()

#NAVIGATE_IN_FILESYSTEM
            while True:
                home_directory_dict = list_directory(current_directory)

                print(f"Current directory: {current_directory}")
                print_directory_list(home_directory_dict)

                user_target_dir = ask_dir_from_list(
                    home_directory_dict,
                    count_dir_len(home_directory_dict)
                )

                if user_target_dir is None:
                    break

                if user_target_dir == 0:
                    current_directory = current_directory.parent
                    continue

                current_directory = navigate_in_filesystem(
                    home_directory_dict,
                    user_target_dir
                )

                print(f"Current directory: {current_directory}")
                print_directory_list(list_directory(current_directory))

                input("Press Enter to continue...")


if __name__ == "__main__":
    main()
