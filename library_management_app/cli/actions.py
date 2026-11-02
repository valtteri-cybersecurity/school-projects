import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "data" / "book_register.json"

def save_books(books: dict) -> None:
    old_books = load_books()

    for book, details in books.items():
        if book in old_books:
            raise ValueError(f"Book '{book}' already exists!")

        old_books[book] = details

    FILE_PATH.write_text(
        json.dumps(old_books, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

def load_books() -> dict:
    if not FILE_PATH.exists():
        return {}

    content = FILE_PATH.read_text(encoding="utf-8")

    books = json.loads(content)

    if not isinstance(books, dict):
        raise ValueError("Invalid book register format!")

    return books

def list_books():
    if not FILE_PATH.exists():
        print("Book register does not exist!")
        return  
    books = load_books()

    if not books:
        print("Book register is empty!")
        return
    
    for book, details in books.items():
        print(f"\nBook: {book}")

        for key, value in details.items():
            print(f"   {key:<12} | {value}")

def search_by_name():
    if not FILE_PATH.exists():
        print("Book register does not exist!")
        return
    
    books = load_books()

    if not books:
        print("Book register is empty!")
        return
    
    while True:
        try:
            search = input("Give name of the book (or 'exit' to return): ").strip().lower()
            if search == "exit":
                return

            if search == "":
                print("This column cant be empty!")
                continue
            elif search.isdigit():
                print("Book name cannot contain only numbers!")
                continue
            
            else:
                found = False

                for book, details in books.items():
                    if search in book.lower():
                        print(f"\nBook: {book}")

                        for key, value in details.items():
                            print(f"   {key:<12} | {value}")
                        
                        found = True

                if not found:
                    print(f"\nNo books found matching: '{search}'.")
        
        except ValueError as e:
            print(f"Error: {e}")

def search_by_author():
    if not FILE_PATH.exists():
        print("Book register does not exist!")
        return

    books = load_books()

    if not books:
        print("Book register is empty!")
        return

    while True:
        try:
            search = input("Give name of the author (or 'exit' to return): ").strip().lower()
            if search == "exit":
                return

            if search == "":
                print("This column cant be empty!")
                continue

            elif search.isdigit():
                print("This column cant be only number!")
                continue

            else:
                found = False

                for book, details in books.items():
                    if search in details["author"].lower():
                        print(f"\nBook: {book}")

                        for key, value in details.items():
                            print(f"   {key:<12} | {value}")

                        found = True

                if not found:
                    print(f"\nNo authors found matching: '{search}'.")

        except ValueError as e:
            print(f"Error: {e}")