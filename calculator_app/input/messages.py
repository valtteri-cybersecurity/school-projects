################
# Error messages

def program_shutting_down() -> None:
    print("Info: Program shutting down...")

def only_numbers_allowed() -> None:
    print("Error: Only numbers allowed!")

def cant_divide_with_zero() -> None:
    print("Error: Cant divide with zero!")

# Math result message
def show_operation(a: int, b: int, operator: str, result: int) -> None:
    print(f"Result: {a} {operator} {b} = {result}")

