import pytest

from app.models.book import Book
from app.repositories.book_repository import BookRepository


def test_add_book():
    repository = BookRepository()
    book = Book(1, "Python", "Matti", 2025, True)

    repository.add(book)

    assert 1 in repository.books
    assert repository.books[1] is book


def test_add_multiple_books():
    repository = BookRepository()

    book1 = Book(1, "Python", "Matti", 2025, True)
    book2 = Book(2, "Linux", "Liisa", 2024, False)

    repository.add(book1)
    repository.add(book2)

    assert len(repository.books) == 2
    assert repository.books[1] is book1
    assert repository.books[2] is book2


def test_duplicate_book_id():
    repository = BookRepository()

    book1 = Book(1, "Python", "Matti", 2025, True)
    book2 = Book(1, "Linux", "Liisa", 2024, False)

    repository.add(book1)

    with pytest.raises(ValueError, match="Book ID already exists!"):
        repository.add(book2)

    assert len(repository.books) == 1
    assert repository.books[1] is book1


def test_search_by_author():
    repository = BookRepository()

    book1 = Book(1, "Python", "Matti Virtanen", 2025, True)
    book2 = Book(2, "Linux", "Matti Virtanen", 2024, False)
    book3 = Book(3, "MySQL", "Kalle Jokinen", 2020, True)

    repository.add(book1)
    repository.add(book2)
    repository.add(book3)

    result = repository.search_by_author("Matti")

    assert len(result) == 2
    assert book1 in result
    assert book2 in result
    assert book3 not in result


def test_get_by_id_returns_book():
    repository = BookRepository()
    book1 = Book(1, "Python", "Matti", 2025, True)
    book2 = Book(2, "Linux", "Liisa", 2024, False)

    repository.add(book1)
    repository.add(book2)

    result = repository.get_by_id(2)

    assert result is book2


def test_get_by_id_returns_none_for_missing_book():
    repository = BookRepository()
    book = Book(1, "Python", "Matti", 2025, True)

    repository.add(book)

    result = repository.get_by_id(99)

    assert result is None


def test_get_all_returns_empty_list():
    repository = BookRepository()

    result = repository.get_all()

    assert result == []


def test_get_all_returns_added_books():
    repository = BookRepository()
    book1 = Book(1, "Python", "Matti", 2025, True)
    book2 = Book(2, "Linux", "Liisa", 2024, False)

    repository.add(book1)
    repository.add(book2)

    result = repository.get_all()

    assert len(result) == 2
    assert book1 in result
    assert book2 in result


def test_search_by_title_returns_partial_match():
    repository = BookRepository()
    book1 = Book(1, "Python", "Matti", 2025, True)
    book2 = Book(2, "Linux", "Liisa", 2024, False)

    repository.add(book1)
    repository.add(book2)

    result = repository.search_by_title("thon")

    assert result == [book1]


def test_search_by_title_returns_empty_list_for_unknown_title():
    repository = BookRepository()
    book = Book(1, "Python", "Matti", 2025, True)

    repository.add(book)

    result = repository.search_by_title("Java")

    assert result == []
