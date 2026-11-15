import pytest

from app.models.book import Book
from app.repositories import mysql_book_repository
from app.repositories.mysql_book_repository import MySQLBookRepository


@pytest.mark.parametrize("available", [0, 1])
def test_row_to_book(available):
    row = {
        "book_id": 17,
        "title": "Python",
        "author": "Matti",
        "year": 2025,
        "available": available,
    }

    book = MySQLBookRepository()._row_to_book(row)

    assert book.to_dict() == {**row, "available": bool(available)}
    assert book.available is bool(available)


@pytest.mark.parametrize("method", ["search_by_title", "search_by_author"])
@pytest.mark.parametrize("term", ["", "   "])
def test_empty_search_does_not_open_connection(monkeypatch, method, term):
    def unexpected_connection():
        raise AssertionError("Empty search must not open a connection")

    monkeypatch.setattr(
        mysql_book_repository, "get_connection", unexpected_connection
    )

    assert getattr(MySQLBookRepository(), method)(term) == []


class WriteCursor:
    lastrowid = 17
    rowcount = 1

    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, values):
        self.connection.sql = sql
        self.connection.values = values
        if self.connection.failure == "execute":
            raise RuntimeError("Write failed")


class WriteConnection:
    def __init__(self, failure):
        self.failure = failure
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        return WriteCursor(self)

    def commit(self):
        self.commits += 1
        if self.failure == "commit":
            raise RuntimeError("Write failed")

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


@pytest.mark.parametrize("method", ["add", "set_availability"])
@pytest.mark.parametrize("failure", [None, "execute", "commit"])
def test_write_transaction_and_parameters(monkeypatch, method, failure):
    connection = WriteConnection(failure)
    monkeypatch.setattr(
        mysql_book_repository, "get_connection", lambda: connection
    )
    repository = MySQLBookRepository()
    book = Book(None, "Python's basics", "O'Connor", 2025, True)

    if method == "add":
        arguments = (book,)
        expected_values = (book.title, book.author, book.year, book.available)
    else:
        arguments = (17, False)
        expected_values = (False, 17)

    if failure:
        with pytest.raises(RuntimeError, match="Write failed"):
            getattr(repository, method)(*arguments)
    else:
        result = getattr(repository, method)(*arguments)
        if method == "add":
            assert result.to_dict() == {**book.to_dict(), "book_id": 17}
        else:
            assert result is True

    assert connection.values == expected_values
    assert "Python's basics" not in connection.sql
    assert connection.commits == (0 if failure == "execute" else 1)
    assert connection.rollbacks == (1 if failure else 0)
    assert connection.closed is True
