from input.user_input import ask_action_1

def test_choice_one(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "1")
    result = ask_action_1()
    assert result == 1

def test_choice_two(monkeypatch):
    monkeypatch.setattr(
        "builtins.input", lambda prompt: "2")
    result = ask_action_1()
    assert result == 2

def test_invalid_number(monkeypatch):
    inputs = iter(["3", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    result = ask_action_1()
    assert result == 1

def test_invalid_text(monkeypatch):
    inputs = iter(["abc", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    result = ask_action_1()
    assert result == 2
