import pytest

from installer.migrations import validate_books_schema


class SchemaCursor:
    def __init__(self, columns, primary_key):
        self.columns = columns
        self.primary_key = primary_key
        self.sql = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql):
        assert sql.strip().upper().startswith("SELECT")
        self.sql = sql

    def fetchall(self):
        if "information_schema.statistics" in self.sql:
            return [{"name": name} for name in self.primary_key]
        return self.columns


class SchemaConnection:
    def __init__(self, columns, primary_key):
        self.columns = columns
        self.primary_key = primary_key

    def cursor(self):
        return SchemaCursor(self.columns, self.primary_key)


@pytest.fixture
def schema_connection():
    columns = []

    for name, data_type, column_type, length in [
        ("book_id", "bigint", "bigint unsigned", None),
        ("title", "varchar", "varchar(100)", 100),
        ("author", "varchar", "varchar(100)", 100),
        ("year", "smallint", "smallint unsigned", None),
        ("available", "tinyint", "tinyint(1)", None),
        ("created_at", "datetime", "datetime(6)", None),
        ("updated_at", "datetime", "datetime(6)", None),
    ]:
        columns.append({
            "name": name,
            "data_type": data_type,
            "column_type": column_type,
            "max_length": length,
        })

    return SchemaConnection(columns, ["book_id"])


def test_valid_books_schema_is_accepted(schema_connection):
    assert validate_books_schema(schema_connection) is None


def test_missing_books_table_is_rejected(schema_connection):
    schema_connection.columns = []

    with pytest.raises(RuntimeError, match="Missing books table"):
        validate_books_schema(schema_connection)


@pytest.mark.parametrize(
    "name", ["book_id", "title", "author", "year", "available",
             "created_at", "updated_at"]
)
def test_missing_column_is_rejected(schema_connection, name):
    schema_connection.columns = [
        row for row in schema_connection.columns if row["name"] != name
    ]

    with pytest.raises(RuntimeError, match=f"Missing books column: {name}"):
        validate_books_schema(schema_connection)


@pytest.mark.parametrize(
    "name, field, value",
    [
        ("author", "data_type", "int"),
        ("title", "max_length", 50),
        ("book_id", "column_type", "bigint"),
        ("year", "column_type", "smallint"),
        ("available", "data_type", "varchar"),
        ("created_at", "data_type", "timestamp"),
        ("updated_at", "data_type", "timestamp"),
    ]
)
def test_wrong_column_type_is_rejected(
    schema_connection, name, field, value
):
    for column in schema_connection.columns:
        if column["name"] == name:
            column[field] = value

    with pytest.raises(RuntimeError, match="Unexpected column type"):
        validate_books_schema(schema_connection)


@pytest.mark.parametrize("primary_key", [[], ["title"], ["book_id", "title"]])
def test_wrong_primary_key_is_rejected(schema_connection, primary_key):
    schema_connection.primary_key = primary_key

    with pytest.raises(RuntimeError, match="Unexpected books primary key"):
        validate_books_schema(schema_connection)
