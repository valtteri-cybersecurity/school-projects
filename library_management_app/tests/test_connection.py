import importlib
from pathlib import Path

import pytest

from database import connection


def test_repository_import_does_not_open_connection(monkeypatch):
    def unexpected_connection(*args, **kwargs):
        raise AssertionError("Import must not open a database connection")

    monkeypatch.setattr(
        connection.pymysql, "connect", unexpected_connection
    )

    importlib.reload(connection)
    repository = importlib.import_module(
        "app.repositories.mysql_book_repository"
    )
    importlib.reload(repository)

    assert repository.get_connection is connection.get_connection


def test_env_file_is_in_application_directory():
    application_dir = Path(__file__).resolve().parents[1]

    assert connection.ENV_PATH == application_dir / ".env"


@pytest.mark.parametrize(
    "missing_vars",
    [
        ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"],
        ["DB_HOST"],
        ["DB_PASSWORD"],
    ]
)
def test_missing_settings_are_reported_before_connecting(
    monkeypatch, missing_vars
):
    for name in ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
        monkeypatch.setenv(name, "test_value")

    for name in missing_vars:
        monkeypatch.delenv(name)

    def unexpected_connection(*args, **kwargs):
        raise AssertionError("Missing settings must prevent connection")

    monkeypatch.setattr(
        connection.pymysql, "connect", unexpected_connection
    )

    with pytest.raises(RuntimeError) as error:
        connection.get_connection()

    assert str(error.value) == (
        "Missing environment variables: " + ", ".join(missing_vars)
    )
