from app.models.book import Book

class BookRepository:
    def __init__(self):
        self.books = {}

    def add(self, book: Book):
        if book.book_id in self.books:
            raise ValueError("Book ID already exists!")

        self.books[book.book_id] = book
    
    def get_by_id(self, book_id: int):
        result = self.books.get(book_id)
        return result
    
    def get_all(self):
        books_list = []
        for book in self.books.values():
            books_list.append(book)
        return books_list
    
    def search_by_title(self, title: str):
        books_list = []

        title = title.strip()
        if title == "":
            return books_list

        for book in self.books.values():
            if title.casefold() in book.title.casefold():
                books_list.append(book)
        return books_list

    def search_by_author(self, author: str):
        books_list = []

        author = author.strip()
        if author == "":
            return books_list
        
        for book in self.books.values():
            if author.casefold() in book.author.casefold():
                books_list.append(book)
        return books_list