from gui.menu import mainmenu, mainmenu_nav
from input.user_input import ask_numbers
from input.messages import program_shutting_down
from input.messages import show_operation
from operations.math_functions import add, subtract, multiply, divide


def main():
    while True:
        mainmenu()
        nav1 = mainmenu_nav()

        if nav1 == 0:
            program_shutting_down()
            break

        numbers = ask_numbers()
        num1 = numbers[0]
        num2 = numbers[1]
                 
        if nav1 == 1:
            operator = "+"
            result = add(num1, num2)
            show_operation(num1, num2, operator, result)
            continue
        elif nav1 == 2:
            operator = "-"
            result = subtract(num1, num2)
            show_operation(num1, num2, operator, result)
            continue
        elif nav1 == 3:
            operator = "*"
            result = multiply(num1, num2)
            show_operation(num1, num2, operator, result)
            continue
        elif nav1 == 4:
            operator = "/"
            try:
                result = divide(num1, num2)
            except ValueError as error:
                print(f"Error: {error}")
                continue

            show_operation(num1, num2, operator, result)
            continue

if __name__=="__main__":
    main()