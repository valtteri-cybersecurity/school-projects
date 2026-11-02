import pytest

from installer.migrations import (
    calculate_checksum,
    create_migration_table,
    get_migration_files,
    read_migration_sql,
    run_migrations,
    start_migration_attempt,
    mark_migration_failed,
)

from installer.migration_lock import migration_lock


def test_fresh_install_and_second_run_preserve_book(
    mysql_connections
):
    connection, _ = mysql_connections

    first = run_migrations(connection)

    assert first == {
        "applied": ["001"],
        "skipped": []
    }

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO books (title, author, year)
            VALUES (%s, %s, %s)
            """,
            ("Python", "Matti", 2025)
        )

    connection.commit()

    second = run_migrations(connection)

    assert second == {
        "applied": [],
        "skipped": ["001"]
    }

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT title, author FROM books"
        )
        rows = cursor.fetchall()

        cursor.execute(
            "SELECT status FROM migration_attempts"
        )
        attempts = cursor.fetchall()

    assert rows == [
        {"title": "Python", "author": "Matti"}
    ]

    assert attempts == [
        {"status": "APPLIED"}
    ]


def test_unfinished_migration_blocks_rerun(
    mysql_connections
):
    connection, _ = mysql_connections

    migration_file = get_migration_files()[0]

    create_migration_table(connection)

    version = "001"
    checksum = calculate_checksum(migration_file)

    start_migration_attempt(
        connection,
        version,
        checksum
    )

    sql = read_migration_sql(migration_file)

    with connection.cursor() as cursor:
        cursor.execute(sql)

    with pytest.raises(
        RuntimeError,
        match="Unresolved migration"
    ):
        run_migrations(connection)

    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'books'")
        assert cursor.fetchone() is not None


def test_failed_migration_blocks_rerun(
    mysql_connections
):
    connection, _ = mysql_connections

    migration_file = get_migration_files()[0]

    create_migration_table(connection)

    checksum = calculate_checksum(migration_file)

    attempt_id = start_migration_attempt(
        connection,
        "001",
        checksum
    )

    mark_migration_failed(
        connection,
        attempt_id,
        "Simulated failure"
    )

    with pytest.raises(
        RuntimeError,
        match="Unresolved migration"
    ):
        run_migrations(connection)


def test_modified_checksum_blocks_rerun(
    mysql_connections
):
    connection, _ = mysql_connections

    run_migrations(connection)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE schema_migrations
            SET checksum = %s
            WHERE version = %s
            """,
            ("0" * 64, "001")
        )

    connection.commit()

    with pytest.raises(
        RuntimeError,
        match="Checksum mismatch"
    ):
        run_migrations(connection)


def test_lock_blocks_second_connection(
    mysql_connections
):
    first, second = mysql_connections

    with migration_lock(first, timeout=1):

        with pytest.raises(
            RuntimeError,
            match="Unable to acquire"
        ):
            with migration_lock(second, timeout=0):
                pass

    with migration_lock(second, timeout=0):
        pass

def test_missing_books_table_is_rejected(mysql_connections):
    connection, _ = mysql_connections

    run_migrations(connection)

    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE books")

    with pytest.raises(RuntimeError, match="Missing books column"):
        run_migrations(connection)


def test_modified_books_column_is_rejected(mysql_connections):
    connection, _ = mysql_connections

    run_migrations(connection)

    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE books MODIFY author INT NOT NULL"
        )

    with pytest.raises(RuntimeError, match="Unexpected column type"):
        run_migrations(connection)

def test_missing_books_table_is_rejected(mysql_connections):
    connection, _ = mysql_connections

    run_migrations(connection)

    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE books")

    with pytest.raises(RuntimeError, match="Missing books column"):
        run_migrations(connection)

def test_modified_books_column_is_rejected(mysql_connections):
    connection, _ = mysql_connections

    run_migrations(connection)

    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE books MODIFY author INT NOT NULL"
        )

    with pytest.raises(RuntimeError, match="Unexpected column type"):
        run_migrations(connection)