
from contextlib import nullcontext

import pytest

from installer import migrations


@pytest.fixture
def migration_file(tmp_path):
    file_path = tmp_path / "001_initial_schema.sql"
    file_path.write_text(
        "CREATE TABLE IF NOT EXISTS books (id INT);",
        encoding="utf-8"
    )
    return file_path


def fake_history(monkeypatch, applied, incomplete=None):
    if incomplete is None:
        incomplete = []

    monkeypatch.setattr(
        migrations,
        "get_applied_migrations",
        lambda connection: applied
    )

    monkeypatch.setattr(
        migrations,
        "get_incomplete_migrations",
        lambda connection: incomplete
    )


def test_new_installation_is_valid(monkeypatch, migration_file):
    fake_history(monkeypatch, {})

    result = migrations.validate_migration_history(
        None, [migration_file]
    )

    assert result is None


def test_matching_history_is_valid(monkeypatch, migration_file):
    checksum = migrations.calculate_checksum(migration_file)
    fake_history(monkeypatch, {"001": checksum})

    result = migrations.validate_migration_history(
        None, [migration_file]
    )

    assert result is None


def test_changed_checksum_is_rejected(monkeypatch, migration_file):
    fake_history(monkeypatch, {"001": "0" * 64})

    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        migrations.validate_migration_history(
            None, [migration_file]
        )


@pytest.mark.parametrize("status", ["RUNNING", "FAILED"])
def test_unresolved_attempt_is_rejected(
    monkeypatch, migration_file, status
):
    attempts = [
        {
            "attempt_id": 12,
            "version": "001",
            "status": status
        }
    ]

    fake_history(monkeypatch, {}, attempts)

    with pytest.raises(RuntimeError, match="Unresolved migration"):
        migrations.validate_migration_history(
            None, [migration_file]
        )


def test_unknown_version_is_rejected(monkeypatch, migration_file):
    fake_history(monkeypatch, {"999": "0" * 64})

    with pytest.raises(RuntimeError, match="Unknown applied"):
        migrations.validate_migration_history(
            None, [migration_file]
        )


def test_history_gap_is_rejected(
    monkeypatch, migration_file, tmp_path
):
    second = tmp_path / "002_add_index.sql"

    second.write_text(
        "CREATE INDEX ix ON books (id);",
        encoding="utf-8"
    )

    checksum = migrations.calculate_checksum(second)
    fake_history(monkeypatch, {"002": checksum})

    with pytest.raises(RuntimeError, match="gap"):
        migrations.validate_migration_history(
            None, [migration_file, second]
        )


def test_invalid_filename_is_rejected(monkeypatch, tmp_path):
    file_path = tmp_path / "bad_migration.sql"
    file_path.write_text("SELECT 1;", encoding="utf-8")

    fake_history(monkeypatch, {})

    with pytest.raises(ValueError):
        migrations.validate_migration_history(
            None, [file_path]
        )


class EmptyCursor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, values=None):
        pass

    def fetchall(self):
        return []


class EmptyConnection:
    def cursor(self):
        return EmptyCursor()


def test_run_stops_before_apply_on_invalid_history(
    monkeypatch, migration_file
):
    monkeypatch.setattr(
        migrations, "get_migration_files",
        lambda: [migration_file]
    )

    monkeypatch.setattr(
        migrations, "migration_lock",
        lambda connection: nullcontext()
    )

    monkeypatch.setattr(
        migrations, "create_migration_table",
        lambda connection: None
    )

    def reject_history(connection, files):
        raise RuntimeError("Invalid migration history")

    def unexpected_apply(connection, file_path):
        raise AssertionError("SQL execution should not start")

    monkeypatch.setattr(
        migrations, "validate_migration_history",
        reject_history
    )

    monkeypatch.setattr(
        migrations, "apply_migration",
        unexpected_apply
    )

    with pytest.raises(RuntimeError, match="Invalid migration history"):
        migrations.run_migrations(EmptyConnection())


class FailingDDLCursor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, values=None):
        if "IS_USED_LOCK" in sql:
            return

        if sql.strip().upper().startswith("CREATE TABLE"):
            raise RuntimeError("Simulated DDL failure")

    def fetchone(self):
        return {"lock_owner": 77, "connection_id": 77}


class FailingDDLConnection:
    def cursor(self):
        return FailingDDLCursor()


def test_ddl_failure_records_failed_attempt(
    monkeypatch, migration_file, tmp_path
):
    from installer import migration_lock as lock_module

    failed = []
    applied = []

    monkeypatch.setattr(migrations, "MIGRATIONS_DIR", tmp_path)
    monkeypatch.setattr(
        migrations, "get_migration_files",
        lambda: [migration_file]
    )
    monkeypatch.setattr(
        migrations, "validate_migration_history",
        lambda connection, files: None
    )
    monkeypatch.setattr(
        migrations, "get_applied_migrations",
        lambda connection: {}
    )
    monkeypatch.setattr(
        migrations, "check_initial_schema",
        lambda connection: None
    )
    monkeypatch.setattr(
        migrations, "start_migration_attempt",
        lambda *args: 42
    )
    monkeypatch.setattr(
        migrations, "mark_migration_failed",
        lambda *args: failed.append(args)
    )
    monkeypatch.setattr(
        migrations, "mark_migration_applied",
        lambda *args: applied.append(args)
    )
    monkeypatch.setattr(
        lock_module, "get_lock_name",
        lambda connection: "test_lock"
    )

    with pytest.raises(RuntimeError, match="requires verification"):
        migrations.apply_migration(
            FailingDDLConnection(), migration_file
        )

    assert len(failed) == 1
    assert failed[0][1] == 42
    assert applied == []


def test_multiple_sql_statements_are_rejected(tmp_path):
    file_path = tmp_path / "001_initial_schema.sql"
    file_path.write_text(
        "SELECT 1; SELECT 2;",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="exactly one SQL statement"):
        migrations.read_migration_sql(file_path)
