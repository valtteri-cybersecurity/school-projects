from input.messages import only_numbers_allowed

def ask_numbers() -> list:
    numbers = []
    while True:
        first_number = input("Give first number: ")
        if not first_number.isdigit():
            only_numbers_allowed()
            continue
        first_number = int(first_number)
        numbers.append(first_number)

        second_number = input("Give second number: ")
        if not second_number.isdigit():
            only_numbers_allowed()
            continue
        second_number = int(second_number)
        numbers.append(second_number)

        return numbers

def ask_operation() -> str:
    choice = input("Chooce math operations 1-4 or 0 to quit: ")
    return choice
            