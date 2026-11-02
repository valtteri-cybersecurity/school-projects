import os

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def main_menu():
    print("\n\nWelcome to virtual library!\n")
    print("1. Save books in library")
    print("2. List books of the library")
    print("3. Search avaibility of book by book-name")
    print("4. Search avaibility of book(s) by author-name")
    print("5. Quit program")

def main_menu_navigation():
    while True:
        try:
            choice = int(input("Select number of the action: "))

        except ValueError:
            print("Only numbers are allowed!")
            continue

        if 1 <= choice <= 5:
            return choice

        print("Choose a number between 1 and 5!")
            


