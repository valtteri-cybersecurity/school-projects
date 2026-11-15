import stat

import pymysql
import pytest

from installer import setup_database as setup


def test_generated_password_is_random_and_has_character_groups():
    password = setup.generate_password()

    assert len(password) >= 36
    assert password != setup.generate_password()
    assert any(character.islower() for character in password)
    assert any(character.isupper() for character in password)
    assert any(character.isdigit() for character in password)
    assert any(not character.isalnum() for character in password)


@pytest.mark.parametrize(
    "database_name, user_name",
    [("mysql", "library_user"), ("library; DROP DATABASE mysql", "library_user"),
     ("Library", "library_user"), ("library", "bad'user"),
     ("library", "a" * 33), ("sys", "library_user")]
)
def test_invalid_names_are_rejected(database_name, user_name):
    with pytest.raises(ValueError):
        setup.validate_names(database_name, user_name)


def test_env_content_preserves_other_settings():
    original = '# Keep this comment\nFEATURE="hello world"\nDB_PASSWORD=old\nexport DB_USER=old\n'
    settings = {
        "DB_HOST": "127.0.0.1", "DB_PORT": "3306", "DB_NAME": "library",
        "DB_USER": "library_user", "DB_PASSWORD": "Aa1!test_password",
    }

    content = setup.env_content(original, settings)

    assert '# Keep this comment\nFEATURE="hello world"' in content
    assert "=old" not in content
    for key, value in settings.items():
        assert content.count(key + "=") == 1
        assert f"{key}={value}\n" in content


def test_pending_file_is_private_and_not_overwritten(tmp_path):
    path = tmp_path / ".env.setup-pending"
    setup.write_pending(path, "DB_PASSWORD=test_password\n")

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    with pytest.raises(FileExistsError):
        setup.write_pending(path, "replacement")
    assert path.read_text() == "DB_PASSWORD=test_password\n"


def test_pending_file_blocks_retry_before_mysql_access(tmp_path):
    pending = tmp_path / ".env.setup-pending"
    pending.write_text("recovery data")

    with pytest.raises(RuntimeError, match="Pending setup credentials"):
        setup.setup_database(None, tmp_path / ".env")

    assert pending.read_text() == "recovery data"


def test_env_symlink_is_rejected(tmp_path):
    target = tmp_path / "other_file"
    target.write_text("untouched")
    env_path = tmp_path / ".env"
    env_path.symlink_to(target)

    with pytest.raises(RuntimeError, match="symbolic links"):
        setup.setup_database(None, env_path)

    assert target.read_text() == "untouched"


def test_different_configuration_is_preserved(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("DB_NAME=another_database\n")

    with pytest.raises(RuntimeError, match="Existing DB_NAME differs"):
        setup.setup_database(None, env_path)

    assert env_path.read_text() == "DB_NAME=another_database\n"


@pytest.mark.parametrize("port", [0, 65536, True, "3306"])
def test_invalid_port_is_rejected(tmp_path, port):
    with pytest.raises(ValueError, match="Port must"):
        setup.setup_database(None, tmp_path / ".env", port=port)


def test_cli_does_not_print_administrator_password(monkeypatch, capsys):
    secret = "private_administrator_password"
    monkeypatch.setattr("sys.argv", ["setup_database"])
    monkeypatch.setattr(setup.getpass, "getpass", lambda prompt: secret)

    def connection_failure(**options):
        assert options["password"] == secret
        raise pymysql.err.OperationalError(1045, "Rejected password: " + secret)

    monkeypatch.setattr(setup.pymysql, "connect", connection_failure)

    assert setup.main() == 1
    output = capsys.readouterr()
    assert secret not in output.out + output.err
    assert "Setup failed" in output.out
