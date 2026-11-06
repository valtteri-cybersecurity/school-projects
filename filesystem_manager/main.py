from app.cli.user_input import ask_creation_mode, ask_saving_location, ask_newdir_name
from app.services.directory_service import dir_exists, create_new_dir

def main():
    creation_mode = ask_creation_mode()

    if creation_mode == 1:
        location = ask_saving_location()
        if dir_exists(location):
            newdir_name = ask_newdir_name(location)
            create_new_dir(newdir_name)
        else:
            print(f"Directory: {location} does not exist!")



if __name__ == "__main__":
    main()