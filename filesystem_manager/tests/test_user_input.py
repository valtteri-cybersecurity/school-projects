from app.cli.user_input import (
    three_option_navigation,
    ask_saving_location,
    ask_dir_from_list
)

#################################################################################

# test: three_option_navigation

def test_navigation_choice_one(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "1")
    result = three_option_navigation()
    assert result == 1


def test_navigation_choice_two(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "2")
    result = three_option_navigation()
    assert result == 2


def test_navigation_choice_zero(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "0")
    result = three_option_navigation()
    assert result is None


def test_navigation_invalid_number(monkeypatch):
    inputs = iter(["3", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    result = three_option_navigation()
    assert result == 1


def test_navigation_invalid_text(monkeypatch):
    inputs = iter(["abc", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    result = three_option_navigation()
    assert result == 2


#################################################################################

# test: ask_saving_location

def test_saving_location(monkeypatch, tmp_path):
    test_dir = tmp_path / "Documents"
    test_dir.mkdir()

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda prompt: "Documents")

    result = ask_saving_location()

    assert result == str(test_dir)


def test_saving_location_cancel(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "0")

    result = ask_saving_location()

    assert result is None


#################################################################################

# test: ask_dir_from_list

def test_directory_choice_one(monkeypatch):
    directories = {1: "Documents", 2: "Downloads"}

    monkeypatch.setattr("builtins.input", lambda prompt: "1")

    result = ask_dir_from_list(directories, len(directories))

    assert result == 1


def test_directory_choice_two(monkeypatch):
    directories = {1: "Documents", 2: "Downloads"}

    monkeypatch.setattr("builtins.input", lambda prompt: "2")

    result = ask_dir_from_list(directories, len(directories))

    assert result == 2


def test_directory_choice_parent(monkeypatch):
    directories = {1: "Documents", 2: "Downloads"}

    monkeypatch.setattr("builtins.input", lambda prompt: "0")

    result = ask_dir_from_list(directories, len(directories))

    assert result == 0


def test_directory_choice_menu(monkeypatch):
    directories = {1: "Documents", 2: "Downloads"}

    monkeypatch.setattr("builtins.input", lambda prompt: "q")

    result = ask_dir_from_list(directories, len(directories))

    assert result is None


def test_directory_invalid_number(monkeypatch):
    directories = {1: "Documents", 2: "Downloads"}

    inputs = iter(["3", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    result = ask_dir_from_list(directories, len(directories))

    assert result == 1


def test_directory_invalid_text(monkeypatch):
    directories = {1: "Documents", 2: "Downloads"}

    inputs = iter(["abc", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    result = ask_dir_from_list(directories, len(directories))

    assert result == 2
