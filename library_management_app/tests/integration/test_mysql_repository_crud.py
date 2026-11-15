import pymysql
import pytest

from app.models.book import Book
from app.repositories import mysql_book_repository
from app.repositories.mysql_book_repository import MySQLBookRepository
from installer.migrations import run_migrations


@pytest.fixture
def repository(mysql_connections, monkeypatch):
    connection, _ = mysql_connections
    run_migrations(connection)

    def get_test_connection():
        return pymysql.connect(
            host=connection.host,
            port=connection.port,
            user=connection.user,
            password=connection.password,
            database=connection.db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            connect_timeout=5,
        )

    monkeypatch.setattr(
        mysql_book_repository, "get_connection", get_test_connection
    )
    return MySQLBookRepository()


def test_add_and_read_book_with_generated_id(repository):
    book = Book(None, "Python's basics", "O'Connor", 2025, False)

    saved = repository.add(book)

    assert isinstance(saved.book_id, int)
    assert saved.book_id > 0
    assert saved.to_dict() == {**book.to_dict(), "book_id": saved.book_id}
    assert repository.get_by_id(saved.book_id).to_dict() == saved.to_dict()
    assert [book.to_dict() for book in repository.get_all()] == [saved.to_dict()]


def test_empty_repository_and_missing_id(repository):
    assert repository.get_all() == []
    assert repository.get_by_id(99999) is None
    assert repository.search_by_title("Python") == []
    assert repository.search_by_author("Matti") == []


def test_get_all_orders_by_title_then_id(repository):
    last = repository.add(Book(None, "Zebra", "Matti", 2025))
    first = repository.add(Book(None, "Python", "Liisa", 2024))
    second = repository.add(Book(None, "Python", "Matti", 2023))

    assert [book.book_id for book in repository.get_all()] == [
        first.book_id, second.book_id, last.book_id
    ]


@pytest.mark.parametrize(
    "method, term, expected_titles",
    [
        (
            "search_by_title", "  pYtHoN  ",
            ["Python Advanced", "Python Basics"],
        ),
        ("search_by_author", "  mAt  ", ["Linux", "Python Basics"]),
    ]
)
def test_case_insensitive_partial_search(
    repository, method, term, expected_titles
):
    repository.add(Book(None, "Python Basics", "Matti", 2025))
    repository.add(Book(None, "Linux", "Matti", 2024))
    repository.add(Book(None, "Python Advanced", "Liisa", 2023))
    search = getattr(repository, method)

    assert [book.title for book in search(term)] == expected_titles
    assert search("unknown") == []
    assert search("' OR 1=1 --") == []
    assert search("") == []
    assert search("   ") == []


def test_set_availability_updates_the_correct_book(repository):
    first = repository.add(Book(None, "Python", "Matti", 2025))
    second = repository.add(Book(None, "Linux", "Liisa", 2024))

    assert repository.set_availability(first.book_id, False) is True
    assert repository.get_by_id(first.book_id).available is False
    assert repository.get_by_id(second.book_id).available is True
    assert repository.set_availability(99999, False) is False


def test_failed_add_preserves_existing_books(repository):
    saved = repository.add(Book(None, "Python", "Matti", 2025))

    with pytest.raises(pymysql.err.IntegrityError):
        repository.add(Book(None, None, "Liisa", 2024))

    assert [book.to_dict() for book in repository.get_all()] == [saved.to_dict()]
