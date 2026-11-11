from input.messages import only_numbers_allowed

def ask_numbers() -> list:
    while True:
        numbers = []

        try:
            first_number = int(input("Give first number: "))
            numbers.append(first_number)

            second_number = int(input("Give second number: "))
            numbers.append(second_number)

        except ValueError:
            only_numbers_allowed()
            continue

        return numbers

def ask_operation() -> int:
    while True:
        try:
            choice = int(input("Chooce math operations 1-4 or 0 to quit: "))
        except ValueError:
            only_numbers_allowed()
            continue
        return choice
