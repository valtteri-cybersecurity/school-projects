from app.models.book import Book


def test_create_book():
    book = Book(1, "Python", "Matti", 2025, True)

    assert book.book_id == 1
    assert book.title == "Python"
    assert book.author == "Matti"
    assert book.year == 2025
    assert book.available is True


def test_book_to_dict():
    book = Book(1, "Python", "Matti", 2025, True)

    result = book.to_dict()

    assert result == {
        "book_id": 1,
        "title": "Python",
        "author": "Matti",
        "year": 2025,
        "available": True
    }