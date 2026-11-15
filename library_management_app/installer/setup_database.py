import argparse
import getpass
import os
from pathlib import Path
import re
import secrets
import stat

from dotenv import dotenv_values
import pymysql

from installer.migrations import (
    get_applied_migrations,
    get_migration_files,
    get_migration_version,
    run_migrations,
    validate_books_schema,
    validate_migration_history,
)


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
DB_KEYS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
PLACEHOLDERS = (None, "", "your_password_here", "oma_salasana", "change_me")


def generate_password():
    # Include each character group required by common MySQL password policies.
    return "Aa1!" + secrets.token_urlsafe(32)


def validate_names(database_name, user_name):
    for name in (database_name, user_name):
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", name):
            raise ValueError("Use lowercase letters, digits and underscores in names")
    if database_name in ("mysql", "sys", "information_schema", "performance_schema"):
        raise ValueError("A MySQL system database cannot be used")


def env_content(original, settings):
    lines = []
    for line in original.splitlines():
        if not re.match(r"^\s*(?:export\s+)?DB_(HOST|PORT|NAME|USER|PASSWORD)\s*=", line):
            lines.append(line)
    prefix = "\n".join(lines).rstrip()
    if prefix:
        prefix += "\n\n"
    return prefix + "".join(f"{key}={settings[key]}\n" for key in DB_KEYS)


def write_pending(path, content):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as file:
        os.fchmod(file.fileno(), 0o600)
        file.write(content)
        file.flush()
        os.fsync(file.fileno())


def connect_application(settings):
    return pymysql.connect(
        host=settings["DB_HOST"],
        port=int(settings["DB_PORT"]),
        database=settings["DB_NAME"],
        user=settings["DB_USER"],
        password=settings["DB_PASSWORD"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=False,
    )


def verify_application(admin, settings):
    database_name = settings["DB_NAME"]
    user_name = settings["DB_USER"]
    account = f"`{user_name}`@`127.0.0.1`"
    expected_grants = {
        f"GRANT USAGE ON *.* TO {account}",
        f"GRANT SELECT, INSERT, UPDATE ON `{database_name}`.`books` TO {account}",
    }
    with admin.cursor() as cursor:
        cursor.execute("SHOW GRANTS FOR %s@%s", (user_name, "127.0.0.1"))
        grants = {next(iter(row.values())) for row in cursor.fetchall()}
    if grants != expected_grants:
        raise RuntimeError("Application account has unexpected privileges")

    with connect_application(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT CURRENT_USER() AS account")
            if cursor.fetchone()["account"] != f"{user_name}@127.0.0.1":
                raise RuntimeError("Unexpected application account")
            cursor.execute(
                "SELECT book_id, title, author, year, available FROM books LIMIT 1"
            )
            cursor.fetchall()


def setup_database(
    admin, env_path=ENV_PATH, port=3306,
    database_name="library", user_name="library_user"
):
    validate_names(database_name, user_name)
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")

    env_path = Path(env_path)
    pending_path = env_path.with_name(env_path.name + ".setup-pending")
    if env_path.is_symlink() or pending_path.is_symlink():
        raise RuntimeError("Configuration paths must not be symbolic links")
    if pending_path.exists():
        raise RuntimeError(
            "Pending setup credentials exist. Review the partial installation "
            "before retrying; do not remove the recovery file blindly."
        )

    original = env_path.read_text(encoding="utf-8") if env_path.exists() else None
    values = dotenv_values(env_path, interpolate=False) if original is not None else {}
    settings = {
        "DB_HOST": "127.0.0.1", "DB_PORT": str(port),
        "DB_NAME": database_name, "DB_USER": user_name,
    }
    for key, value in settings.items():
        if values.get(key) not in (None, "", value):
            raise RuntimeError(f"Existing {key} differs from the requested setup")

    with admin.cursor() as cursor:
        cursor.execute(
            "SELECT SCHEMA_NAME FROM information_schema.schemata "
            "WHERE SCHEMA_NAME = %s", (database_name,)
        )
        database_exists = cursor.fetchone() is not None
        cursor.execute(
            "SELECT User FROM mysql.user WHERE User = %s AND Host = %s",
            (user_name, "127.0.0.1"),
        )
        user_exists = cursor.fetchone() is not None

    if values.get("DB_PASSWORD") not in PLACEHOLDERS:
        if not database_exists or not user_exists:
            raise RuntimeError("Existing credentials do not describe a complete installation")
        if stat.S_IMODE(env_path.stat().st_mode) != 0o600:
            raise RuntimeError("Existing .env must have permissions 0600")
        settings["DB_PASSWORD"] = values["DB_PASSWORD"]
        try:
            admin.select_db(database_name)
            files = get_migration_files()
            validate_migration_history(admin, files)
            expected = {get_migration_version(file) for file in files}
            if set(get_applied_migrations(admin)) != expected:
                raise RuntimeError("Installation has unapplied migrations")
            validate_books_schema(admin)
            verify_application(admin, settings)
        except Exception:
            raise RuntimeError(
                "Existing installation could not be verified; no credentials were changed"
            ) from None
        return "existing"

    if database_exists or user_exists:
        raise RuntimeError(
            "Database or application account already exists. "
            "Review it manually; existing objects were not changed."
        )

    settings["DB_PASSWORD"] = generate_password()
    write_pending(pending_path, env_content(original or "", settings))
    try:
        with admin.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4")
        admin.select_db(database_name)
        run_migrations(admin)
        with admin.cursor() as cursor:
            cursor.execute(
                "CREATE USER %s@%s IDENTIFIED BY %s",
                (user_name, "127.0.0.1", settings["DB_PASSWORD"]),
            )
            cursor.execute(
                f"GRANT SELECT, INSERT, UPDATE ON `{database_name}`.`books` TO %s@%s",
                (user_name, "127.0.0.1"),
            )
        verify_application(admin, settings)

        current = env_path.read_text(encoding="utf-8") if env_path.exists() else None
        if env_path.is_symlink() or current != original:
            raise RuntimeError("Configuration changed during setup")
        os.replace(pending_path, env_path)
    except Exception:
        raise RuntimeError(
            "Database setup failed; MySQL may be partially configured. "
            "Recovery credentials remain in the .env.setup-pending file. "
            "The installer did not replace the existing .env."
        ) from None
    return "created"


def main():
    parser = argparse.ArgumentParser(description="Set up the local library MySQL database")
    parser.add_argument("--admin-user", default="root")
    parser.add_argument("--admin-socket", help="Optional local MySQL Unix socket")
    parser.add_argument("--port", type=int, default=3306)
    args = parser.parse_args()

    options = {
        "host": "127.0.0.1", "port": args.port,
        "user": args.admin_user,
        "password": getpass.getpass("MySQL administrator password: "),
        "charset": "utf8mb4", "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 5, "read_timeout": 10, "write_timeout": 10,
        "autocommit": False,
    }
    if args.admin_socket:
        options["unix_socket"] = args.admin_socket
    try:
        with pymysql.connect(**options) as admin:
            result = setup_database(admin, port=args.port)
    except (ValueError, RuntimeError) as error:
        print(str(error))
        return 1
    except (OSError, pymysql.MySQLError):
        # Database exception text can contain credentials; print only a fixed message.
        print(
            "Setup failed. Check administrator access, existing database/account, "
            "configuration permissions and any .env.setup-pending recovery file. "
            "MySQL changes may already have been applied."
        )
        return 1
    if result == "existing":
        print("Existing installation verified. Credentials and books were preserved.")
    else:
        print("Database ready. Application credentials saved to .env. Restart the API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
