def ask_action_1():
    while True:
        try:
            choice = int(input("Create new directory(1) or Create many directories(2): "))
            if choice not in [1,2]:
                print("Choose 1 or 2")
                continue

        except ValueError:
            print("Only numbers allowed.")
            continue

        return choice
