import secrets
import stat

from dotenv import dotenv_values
import pymysql
import pytest

from installer import setup_database as setup


@pytest.fixture
def setup_target(mysql_connections):
    admin, _ = mysql_connections
    name = "library_setup_" + secrets.token_hex(4)
    try:
        yield admin, name, name
    finally:
        with admin.cursor() as cursor:
            cursor.execute("DROP USER IF EXISTS %s@%s", (name, "127.0.0.1"))
            cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")


def install(target, env_path):
    admin, database_name, user_name = target
    return setup.setup_database(
        admin, env_path, port=admin.port,
        database_name=database_name, user_name=user_name,
    )


def test_setup_creates_private_configuration_and_limited_account(setup_target, tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("FEATURE=keep\nDB_PASSWORD=your_password_here\n")

    assert install(setup_target, env_path) == "created"

    values = dotenv_values(env_path, interpolate=False)
    assert values["FEATURE"] == "keep"
    assert values["DB_PASSWORD"] not in setup.PLACEHOLDERS
    assert stat.S_IMODE(env_path.stat().st_mode) == 0o600
    assert not (tmp_path / ".env.setup-pending").exists()

    with setup.connect_application(values) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM books")
            assert cursor.fetchall() == ()
            cursor.execute(
                "INSERT INTO books (title, author, year) VALUES (%s, %s, %s)",
                ("Python", "Matti", 2025),
            )
            cursor.execute("UPDATE books SET available = FALSE")
            connection.commit()
            cursor.execute("SELECT available FROM books")
            assert cursor.fetchone()["available"] == 0

            for sql in [
                "CREATE TABLE forbidden (id INT)",
                "DROP TABLE books",
                "DELETE FROM books",
                "CREATE USER 'forbidden_setup_user'@'127.0.0.1'",
            ]:
                with pytest.raises(pymysql.err.OperationalError):
                    cursor.execute(sql)


def test_second_run_preserves_password_and_books(setup_target, tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    install(setup_target, env_path)
    original = env_path.read_bytes()
    with setup.connect_application(dotenv_values(env_path)) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO books (title, author, year) VALUES (%s, %s, %s)",
                ("Python", "Matti", 2025),
            )
        connection.commit()

    def unexpected_password():
        raise AssertionError("A completed installation must not rotate credentials")

    monkeypatch.setattr(setup, "generate_password", unexpected_password)

    assert install(setup_target, env_path) == "existing"
    assert env_path.read_bytes() == original
    with setup.connect_application(dotenv_values(env_path)) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT title FROM books")
            assert cursor.fetchall() == [{"title": "Python"}]


@pytest.mark.parametrize("existing", ["database", "user"])
def test_unverified_existing_objects_are_not_changed(setup_target, tmp_path, existing):
    admin, database_name, user_name = setup_target
    with admin.cursor() as cursor:
        if existing == "database":
            cursor.execute(f"CREATE DATABASE `{database_name}`")
            cursor.execute(f"CREATE TABLE `{database_name}`.keep_me (id INT)")
        else:
            cursor.execute(
                "CREATE USER %s@%s IDENTIFIED BY %s",
                (user_name, "127.0.0.1", "Aa1!existing_test_password"),
            )
    env_path = tmp_path / ".env"
    env_path.write_text("FEATURE=keep\nDB_PASSWORD=your_password_here\n")
    original = env_path.read_bytes()

    with pytest.raises(RuntimeError, match="already exists"):
        install(setup_target, env_path)

    assert env_path.read_bytes() == original
    assert not (tmp_path / ".env.setup-pending").exists()
    with admin.cursor() as cursor:
        if existing == "database":
            cursor.execute(f"SELECT * FROM `{database_name}`.keep_me")
            assert cursor.fetchall() == ()
        else:
            cursor.execute(
                "SHOW GRANTS FOR %s@%s", (user_name, "127.0.0.1")
            )
            assert len(cursor.fetchall()) == 1


@pytest.mark.parametrize("failure", ["migrations", "verification", "publish"])
def test_failed_setup_keeps_private_recovery_credentials(
    setup_target, tmp_path, monkeypatch, failure
):
    env_path = tmp_path / ".env"
    env_path.write_text("FEATURE=keep\nDB_PASSWORD=your_password_here\n")
    original = env_path.read_bytes()
    secret = "Aa1!private_generated_test_password"
    monkeypatch.setattr(setup, "generate_password", lambda: secret)

    def fail(*args, **kwargs):
        raise RuntimeError("Failure containing password: " + secret)

    if failure == "migrations":
        monkeypatch.setattr(setup, "run_migrations", fail)
    elif failure == "verification":
        monkeypatch.setattr(setup, "verify_application", fail)
    else:
        monkeypatch.setattr(setup.os, "replace", fail)

    with pytest.raises(RuntimeError, match="partially configured") as error:
        install(setup_target, env_path)

    assert secret not in str(error.value)
    assert env_path.read_bytes() == original
    pending_path = tmp_path / ".env.setup-pending"
    assert dotenv_values(pending_path)["DB_PASSWORD"] == secret
    assert stat.S_IMODE(pending_path.stat().st_mode) == 0o600
    with pytest.raises(RuntimeError, match="Pending setup credentials"):
        install(setup_target, env_path)


@pytest.mark.parametrize("change", ["history", "grants", "permissions"])
def test_changed_installation_is_not_repaired_automatically(
    setup_target, tmp_path, change
):
    env_path = tmp_path / ".env"
    install(setup_target, env_path)
    original = env_path.read_bytes()
    admin, database_name, user_name = setup_target
    with admin.cursor() as cursor:
        if change == "history":
            cursor.execute("UPDATE schema_migrations SET checksum = %s", ("0" * 64,))
            admin.commit()
        elif change == "grants":
            cursor.execute(
                f"GRANT CREATE ON `{database_name}`.* TO %s@%s",
                (user_name, "127.0.0.1"),
            )
        else:
            env_path.chmod(0o644)

    with pytest.raises(RuntimeError):
        install(setup_target, env_path)

    assert env_path.read_bytes() == original
    assert not (tmp_path / ".env.setup-pending").exists()


def test_newer_env_changes_are_not_overwritten(setup_target, tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("FEATURE=before\n")
    original_verify = setup.verify_application

    def edit_during_verification(admin, settings):
        original_verify(admin, settings)
        env_path.write_text("FEATURE=after\n")

    monkeypatch.setattr(setup, "verify_application", edit_during_verification)

    with pytest.raises(RuntimeError, match="partially configured"):
        install(setup_target, env_path)

    assert env_path.read_text() == "FEATURE=after\n"
    assert (tmp_path / ".env.setup-pending").is_file()
