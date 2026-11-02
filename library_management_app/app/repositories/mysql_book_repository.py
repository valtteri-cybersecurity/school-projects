from app.database.connection import get_connection
from app.models.book import Book


class MySQLBookRepository:

    def add(self, book: Book):
        connection = get_connection()
    
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO books
                        (name, author, year, available)
                    VALUES (%s, %s, %s, %s)
                """
    
                cursor.execute(
                    sql,
                    (
                        book.title,
                        book.author,
                        book.year,
                        book.available
                    )
                )
    
                book_id = cursor.lastrowid
    
            connection.commit()
    
        except Exception:
            connection.rollback()
            raise
        
        finally:
            connection.close()
    
        return Book(
            book_id,
            book.title,
            book.author,
            book.year,
            book.available
        )

    def get_all(self):
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, author, year, available
                    FROM books
                    ORDER BY name, id
                    """
                )

                rows = cursor.fetchall()

        books = []

        for row in rows:
            book = self._row_to_book(row)
            books.append(book)

        return books

    def get_by_id(self, book_id: int):
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, author, year, available
                    FROM books
                    WHERE id = %s
                    """,
                    (book_id,)
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_book(row)

    def search_by_title(self, title: str):
        title = title.strip()

        if not title:
            return []

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, author, year, available
                    FROM books
                    WHERE name LIKE %s
                    ORDER BY name, id
                    """,
                    ("%" + title + "%",)
                )

                rows = cursor.fetchall()

        books = []

        for row in rows:
            books.append(self._row_to_book(row))

        return books

    def search_by_author(self, author: str):
        author = author.strip()

        if not author:
            return []

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, author, year, available
                    FROM books
                    WHERE author LIKE %s
                    ORDER BY name, id
                    """,
                    ("%" + author + "%",)
                )

                rows = cursor.fetchall()

        books = []

        for row in rows:
            books.append(self._row_to_book(row))

        return books

    def set_availability(self, book_id: int, available: bool):
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE books
                    SET available = %s
                    WHERE id = %s
                    """,
                    (available, book_id)
                )

                updated = cursor.rowcount

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        return updated > 0

    def _row_to_book(self, row):
        return Book(
            row["id"],
            row["name"],
            row["author"],
            row["year"],
            bool(row["available"])
        )
