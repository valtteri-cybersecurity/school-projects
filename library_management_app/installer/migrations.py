from pathlib import Path
import hashlib

from installer.migration_lock import migration_lock


BASE_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = BASE_DIR / "database" / "migrations"

def get_migration_files() -> list[Path]:

    if not MIGRATIONS_DIR.is_dir():
        raise FileNotFoundError(
            f"Migration directory not found: {MIGRATIONS_DIR}"
        )

    migration_files = []

    for file in MIGRATIONS_DIR.glob("*.sql"):
        if file.is_file():
            migration_files.append(file)

    if not migration_files:
        raise ValueError("No SQL migration files found!")

    migration_files.sort(key=lambda file: file.name)

    return migration_files

def calculate_checksum(file_path: Path) -> str:

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Migration file not found: {file_path}"
        )

    file_content = file_path.read_bytes()

    checksum = hashlib.sha256(file_content).hexdigest()

    return checksum

def create_migration_table(connection):

    migrations_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(20) PRIMARY KEY,
            checksum CHAR(64) NOT NULL,
            applied_at DATETIME(6) NOT NULL
                DEFAULT CURRENT_TIMESTAMP(6)
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4;
    """

    attempts_sql = """
        CREATE TABLE IF NOT EXISTS migration_attempts (
            attempt_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            version VARCHAR(20) NOT NULL,
            checksum CHAR(64) NOT NULL,

            status ENUM(
                'RUNNING',
                'APPLIED',
                'FAILED'
            ) NOT NULL DEFAULT 'RUNNING',

            started_at DATETIME(6) NOT NULL
                DEFAULT CURRENT_TIMESTAMP(6),

            finished_at DATETIME(6) NULL,

            error_message TEXT NULL,

            INDEX idx_migration_version (version),
            INDEX idx_migration_status (status)
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4;
    """

    with connection.cursor() as cursor:
        cursor.execute(migrations_sql)
        cursor.execute(attempts_sql)

def get_applied_migrations(connection) -> dict[str, str]:
    applied_migrations = {}

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT version, checksum
            FROM schema_migrations
            ORDER BY version
            """
        )

        results = cursor.fetchall()

    for row in results:
        version = row["version"]
        checksum = row["checksum"]

        applied_migrations[version] = checksum

    return applied_migrations

def get_incomplete_migrations(connection) -> list[dict]:

    sql = """
        SELECT
            attempt_id,
            version,
            checksum,
            status,
            started_at,
            finished_at,
            error_message
        FROM migration_attempts
        WHERE status IN ('RUNNING', 'FAILED')
        ORDER BY started_at ASC, attempt_id ASC
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()

    incomplete_migrations = []

    for row in results:
        incomplete_migrations.append(row)

    return incomplete_migrations

def get_migration_version(file_path: Path) -> str:

    filename = file_path.name

    if not filename.endswith(".sql"):
        raise ValueError(
            f"Invalid migration extension: {filename}"
        )

    filename_without_extension = file_path.stem

    parts = filename_without_extension.split("_", 1)

    if len(parts) != 2:
        raise ValueError(
            f"Invalid migration filename: {filename}"
        )

    version = parts[0]
    description = parts[1]

    if len(version) != 3 or not version.isascii() or not version.isdigit():
        raise ValueError(
            f"Invalid migration version: {version}"
        )

    if not description:
        raise ValueError(
            f"Migration description is missing: {filename}"
        )

    for character in description:
        if character not in "abcdefghijklmnopqrstuvwxyz0123456789_":
            raise ValueError(
                f"Invalid migration description: {filename}"
            )

    return version

def validate_migration_history(
    connection,
    migration_files: list[Path]
) -> None:

    available_migrations = {}
    versions = []

    for file in migration_files:

        version = get_migration_version(file)

        if version in available_migrations:
            raise ValueError(
                f"Duplicate migration version: {version}"
            )

        checksum = calculate_checksum(file)

        available_migrations[version] = checksum
        versions.append(version)

    if not versions:
        raise ValueError("No migration files found!")

    applied_migrations = get_applied_migrations(connection)
    incomplete_migrations = get_incomplete_migrations(connection)

    if incomplete_migrations:
        attempt = incomplete_migrations[0]

        raise RuntimeError(
            "Unresolved migration attempt detected: "
            f"version={attempt['version']}, "
            f"status={attempt['status']}, "
            f"attempt_id={attempt['attempt_id']}"
        )

    for version, stored_checksum in applied_migrations.items():

        if version not in available_migrations:
            raise RuntimeError(
                f"Unknown applied migration version: {version}"
            )

        current_checksum = available_migrations[version]

        if stored_checksum != current_checksum:
            raise RuntimeError(
                f"Checksum mismatch for migration {version}"
            )

    sorted_versions = sorted(versions)

    missing_earlier_version = False

    for version in sorted_versions:

        if version not in applied_migrations:
            missing_earlier_version = True

        elif missing_earlier_version:
            raise RuntimeError(
                "Migration history has a gap before "
                f"version {version}"
            )

def start_migration_attempt(
    connection,
    version: str,
    checksum: str
) -> int:

    sql = """
        INSERT INTO migration_attempts
            (version, checksum, status)
        VALUES (%s, %s, 'RUNNING')
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, (version, checksum))
        attempt_id = cursor.lastrowid

    connection.commit()

    return attempt_id


def mark_migration_applied(
    connection,
    attempt_id: int,
    version: str,
    checksum: str
) -> None:

    insert_sql = """
        INSERT INTO schema_migrations
            (version, checksum)
        VALUES (%s, %s)
    """

    update_sql = """
        UPDATE migration_attempts
        SET status = 'APPLIED',
            finished_at = CURRENT_TIMESTAMP(6)
        WHERE attempt_id = %s
          AND version = %s
          AND checksum = %s
          AND status = 'RUNNING'
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                update_sql,
                (attempt_id, version, checksum)
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Migration attempt is not in RUNNING state!"
                )

            cursor.execute(
                insert_sql,
                (version, checksum)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise


def mark_migration_failed(
    connection,
    attempt_id: int,
    error_message: str
) -> None:

    sql = """
        UPDATE migration_attempts
        SET status = 'FAILED',
            finished_at = CURRENT_TIMESTAMP(6),
            error_message = %s
        WHERE attempt_id = %s
          AND status = 'RUNNING'
    """

    connection.rollback()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                (error_message, attempt_id)
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Unable to mark migration as FAILED!"
                )

        connection.commit()

    except Exception:
        connection.rollback()
        raise


def read_migration_sql(file_path: Path) -> str:

    sql = file_path.read_text(encoding="utf-8-sig").strip()

    if not sql:
        raise ValueError("Migration file is empty!")

    if sql.count(";") != 1 or not sql.endswith(";"):
        raise ValueError(
            "Migration must contain exactly one SQL statement!"
        )

    if "--" in sql or "/*" in sql or "*/" in sql or "#" in sql:
        raise ValueError(
            "SQL comments are not supported in this migration version!"
        )

    statement = sql[:-1].strip()

    if not statement:
        raise ValueError("Migration SQL statement is empty!")

    return statement


def check_initial_schema(connection) -> None:

    sql = """
        SELECT COUNT(*) AS table_count
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name = 'books'
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchone()

    if result is None:
        raise RuntimeError("Unable to inspect database schema!")

    if result["table_count"] != 0:
        raise RuntimeError(
            "The books table already exists without a "
            "verified migration record. Manual review required!"
        )


def apply_migration(connection, migration_file: Path) -> bool:

    version = get_migration_version(migration_file)
    checksum = calculate_checksum(migration_file)

    if version != "001" or migration_file.name != "001_initial_schema.sql":
        raise ValueError(
            "Only 001_initial_schema.sql is supported for now!"
        )

    from installer.migration_lock import get_lock_name

    lock_name = get_lock_name(connection)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT IS_USED_LOCK(%s) AS lock_owner, "
            "CONNECTION_ID() AS connection_id",
            (lock_name,)
        )
        lock_result = cursor.fetchone()

    if (
        lock_result is None
        or lock_result["lock_owner"] is None
        or lock_result["lock_owner"] != lock_result["connection_id"]
    ):
        raise RuntimeError("Migration lock is not held!")

    migration_files = get_migration_files()
    validate_migration_history(connection, migration_files)

    applied = get_applied_migrations(connection)

    if version in applied:
        return False

    sql = read_migration_sql(migration_file)

    normalized_sql = " ".join(sql.upper().split())

    if not normalized_sql.startswith(
        "CREATE TABLE IF NOT EXISTS BOOKS ("
    ):
        raise ValueError(
            "Unexpected initial migration SQL!"
        )

    expected_file = MIGRATIONS_DIR / "001_initial_schema.sql"

    if migration_file.resolve() != expected_file.resolve():
        raise ValueError("Unexpected migration file path!")

    check_initial_schema(connection)

    attempt_id = start_migration_attempt(
        connection,
        version,
        checksum
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)

        mark_migration_applied(
            connection,
            attempt_id,
            version,
            checksum
        )

    except Exception as error:
        try:
            mark_migration_failed(
                connection,
                attempt_id,
                "Migration execution or history recording failed"
            )
        except Exception:
            pass

        raise RuntimeError(
            f"Migration {version} failed. "
            "Database state requires verification."
        ) from error

    return True


def run_migrations(connection) -> dict:

    migration_files = get_migration_files()

    results = {
        "applied": [],
        "skipped": []
    }

    with migration_lock(connection):

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                  AND table_name IN (
                      'books',
                      'schema_migrations',
                      'migration_attempts'
                  )
                """
            )

            existing_rows = cursor.fetchall()

        existing_tables = []

        for row in existing_rows:
            existing_tables.append(row["TABLE_NAME"])

        if "books" in existing_tables:
            if "schema_migrations" not in existing_tables:
                raise RuntimeError(
                    "Existing books table has no migration history!"
                )

        if "schema_migrations" in existing_tables:
            if "migration_attempts" not in existing_tables:
                raise RuntimeError(
                    "Incomplete migration tracking schema!"
                )

        if "migration_attempts" in existing_tables:
            if "schema_migrations" not in existing_tables:
                raise RuntimeError(
                    "Incomplete migration tracking schema!"
                )

        create_migration_table(connection)

        validate_migration_history(
            connection,
            migration_files
        )

        for migration_file in migration_files:

            version = get_migration_version(migration_file)

            applied = apply_migration(
                connection,
                migration_file
            )

            if applied:
                results["applied"].append(version)
            else:
                results["skipped"].append(version)
        
        validate_books_schema(connection)
   
    return results


if __name__ == "__main__":
    files = get_migration_files()

    for file in files:
        checksum = calculate_checksum(file)

        print(f"Migration: {file.name}")
        print(f"SHA-256: {checksum}")
        print()
