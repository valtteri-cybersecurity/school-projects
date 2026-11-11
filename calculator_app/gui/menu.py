from input.messages import only_numbers_allowed
from input.user_input import ask_operation

def mainmenu() -> None:
    print("\n1. Addition\n2. Subtraction\n3. Multiplication\n4. Division\n0. Quit\n")

def mainmenu_nav() -> int:
    while True:
        choice = ask_operation()
        if not choice.isdigit():
            only_numbers_allowed()
            continue
        choice = int(choice)
        if 0 <= choice <= 4:
            return choice