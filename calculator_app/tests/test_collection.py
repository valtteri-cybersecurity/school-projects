import pytest

from operations.math_functions import add, subtract, multiply, divide
from input.messages import show_operation, program_shutting_down, only_numbers_allowed, cant_divide_with_zero
from gui.menu import mainmenu_nav, mainmenu
from input.user_input import ask_numbers
from main import main



#######################################################################
# 1. Math-Function-Tests                                              #  
#######################################################################

def test_add_positive_numbers():
    result = add(5, 3)
    assert result == 8

def test_add_negative_numbers():
    result = add(-10, -2)
    assert result == -12

def test_add_both_types():
    result = add(-2, 2)
    assert result == 0

def test_subtract_positive_numbers():
    result = subtract(10, 5)
    assert result == 5

def test_subtract_negative_numbers():
    result = subtract(-5, -2)
    assert result == -3

def test_subtract_both_types():
    result = subtract(-10, 20)
    assert result == -30

def test_multiply_positive_numbers():
    result = multiply(10, 50)
    assert result == 500

def test_multiply_negative_numbers():
    result = multiply(-2, -10)
    assert result == 20

def test_multiply_both_types():
    result = multiply(5, -2)
    assert result == -10

def test_divide_positive_numbers():
    result = divide(10, 2)
    assert result == 5

def test_divide_negative_numbers():
    result = divide(-100, -10)
    assert result == 10

def test_divide_both_types():
    result = divide(-10, 2)
    assert result == -5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)

#######################################################################
# 2. User-Input-Tests                                                 #  
#######################################################################

def test_ask_numbers_positive(monkeypatch):
    inputs = iter(["5", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = ask_numbers()
    assert result == [5,3]

def test_ask_numbers_zero(monkeypatch):
    inputs = iter(["0", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = ask_numbers()
    assert result == [0, 3]

def test_ask_numbers_negative(monkeypatch):
    inputs = iter(["-5", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = ask_numbers()
    assert result == [-5, 3]

def test_ask_numbers_invalid_input(monkeypatch):
    inputs = iter(["abc", "5", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = ask_numbers()
    assert result == [5,3]

def test_ask_numbers_invalid_second_input(monkeypatch):
    inputs = iter(["5", "abc", "7", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = ask_numbers()

    assert result == [7, 3]

def test_mainmenu_nav_addition(monkeypatch):
    inputs = iter(["1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = mainmenu_nav()
    assert result == 1

def test_mainmenu_nav_quit(monkeypatch):
    inputs = iter(["0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = mainmenu_nav()
    assert result == 0

def test_mainmenu_nav_invalid_text(monkeypatch):
    inputs = iter(["abc", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = mainmenu_nav()
    assert result == 2

def test_mainmenu_nav_invalid_number(monkeypatch):
    inputs = iter(["9", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = mainmenu_nav()
    assert result == 3

def test_mainmenu_nav_negative_number(monkeypatch):
    inputs = iter(["-1", "4"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = mainmenu_nav()
    assert result == 4

def test_show_operation(capsys):
    show_operation(5, 3, "+", 8)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Result: 5 + 3 = 8"

def test_mainmenu(capsys):
    mainmenu()
    captured = capsys.readouterr()
    assert captured.out.strip() == (
        "1. Addition\n"
        "2. Subtraction\n"
        "3. Multiplication\n"
        "4. Division\n"
        "0. Quit"
    )

def test_only_numbers_allowed(capsys):
    only_numbers_allowed()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Error: Only numbers allowed!"

def test_cant_divide_with_zero(capsys):
    cant_divide_with_zero()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Error: Cant divide with zero!"

def test_program_shutting_down(capsys):
    program_shutting_down()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Info: Program shutting down..."

#######################################################################
# 3. Main-Menu tests                                                  #  
#######################################################################

def test_main_quit(monkeypatch, capsys):
    inputs = iter(["0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    captured = capsys.readouterr()

    assert "Info: Program shutting down..." in captured.out


def test_main_addition(monkeypatch, capsys):
    inputs = iter(["1", "5", "3", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    captured = capsys.readouterr()

    assert "Result: 5 + 3 = 8" in captured.out
    assert "Info: Program shutting down..." in captured.out


def test_main_division_by_zero(monkeypatch, capsys):
    inputs = iter(["4", "5", "0", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    captured = capsys.readouterr()

    assert "Error: Cannot divide by zero" in captured.out
    assert "Info: Program shutting down..." in captured.out


def test_main_division(monkeypatch, capsys):
    inputs = iter(["4", "10", "2", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    captured = capsys.readouterr()

    assert "Result: 10 / 2 = 5.0" in captured.out
    assert "Info: Program shutting down..." in captured.out
