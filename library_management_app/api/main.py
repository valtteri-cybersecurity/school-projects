from fastapi import FastAPI

from app.repositories.mysql_book_repository import MySQLBookRepository

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/books")
def get_books():
    repository = MySQLBookRepository()
    books = repository.get_all()
    
    result = []

    for book in books:
        result.append(book.to_dict())

    return result