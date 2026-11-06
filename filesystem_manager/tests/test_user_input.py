from app.cli.user_input import ask_creation_mode, ask_saving_location

#################################################################################

# test: ask_creation_mode

def test_creation_mode_choice_one(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "1")
    result = ask_creation_mode()
    assert result == 1

def test_creation_mode_choice_two(monkeypatch):
    monkeypatch.setattr(
        "builtins.input", lambda prompt: "2")
    result = ask_creation_mode()
    assert result == 2

def test_creation_mode_choice_zero(monkeypatch):
    monkeypatch.setattr(
        "builtins.input", lambda prompt: "0")
    result = ask_creation_mode()
    assert result == 0
    

def test_creation_mode_invalid_number(monkeypatch):
    inputs = iter(["3", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    result = ask_creation_mode()
    assert result == 1

def test_creation_mode_invalid_text(monkeypatch):
    inputs = iter(["abc", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    result = ask_creation_mode()
    assert result == 2

##################################################################################

# test: ask_saving_location

def test_saving_location(monkeypatch, tmp_path):
    test_dir = tmp_path / "Documents"
    test_dir.mkdir()

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda prompt: "Documents")
    result = ask_saving_location()

##################################################################################
