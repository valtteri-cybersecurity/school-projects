from app.cli.ui import print_line, clear_screen, print_empty_line


def print_menu():
    clear_screen()
    print_empty_line(1)
    print_line()
    print_empty_line(1)
    print("1. Create")
    print("2. Show")
    print("0. Quit")
    print_empty_line(1)
    print_line()
    print_empty_line(1)


def print_create_menu():
    clear_screen()
    print_empty_line(1)
    print_line()
    print_empty_line(1)
    print("1. Create directories")
    print("2. Create files")
    print("0. Go back")
    print_empty_line(1)
    print_line()
    print_empty_line(1)


def print_create_dirs_menu():
    clear_screen()
    print_empty_line(1)
    print_line()
    print_empty_line(1)
    print("1. Create directory")
    print("2. Create multiple directories")
    print("0. Go back")
    print_empty_line(1)
    print_line()
    print_empty_line(1)


def print_show_menu():
    clear_screen()
    print_empty_line(1)
    print_line()
    print_empty_line(1)
    print("1. Show Home-directory")
    print("2. Select directory to show")
    print("0. Go back")
    print_empty_line(1)
    print_line()
    print_empty_line(1)


def print_multiple_dirs_menu():
    clear_screen()
    print_empty_line(1)
    print_line()
    print_empty_line(1)
    print("1. Create multiple directories in one location")
    print("2. Create directories in different locations")
    print("0. Go back")
    print_empty_line(1)
    print_line()
    print_empty_line(1)
