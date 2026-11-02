from datetime import date
from cli.actions import load_books

def create_book_details():
    books = {}
    existing_books = load_books()

    current_year = date.today().year

    while True:
        book = input(
            "\nGive name of the book or type 'exit': "
        ).strip()

        if book.lower() == "exit":
            return books

        if not book:
            print("Book name cannot be empty!")
            continue

        if book.isdigit():
            print("Book name cannot contain only numbers!")
            continue

        duplicate = False

        for existing_name in existing_books:
            if book.casefold() == existing_name.casefold():
                duplicate = True
                break

        for new_name in books:
            if book.casefold() == new_name.casefold():
                duplicate = True
                break

        if duplicate:
            print(f"Book '{book}' already exists!")
            continue

        print("\nBook accepted!\n")

        while True:
            author = input(
                f"Give name of author of the book '{book}': "
            ).strip()

            if not author:
                print("Author cannot be empty!")
                continue

            if author.isdigit():
                print("Author name cannot contain only numbers!")
                continue

            print("\nAuthor accepted!\n")
            break

        while True:
            try:
                year = int(
                    input("Give release year: ").strip()
                )

            except ValueError:
                print("Year must be a whole number!")
                continue

            if year < 1450 or year > current_year:
                print("Give a valid release year!")
                continue

            break

        books[book] = {
            "author": author,
            "year": year,
            "available": True
        }

        print("\nBook created successfully!")

        for book_name, details in books.items():
            print(f"\nBook: {book_name}")

            for key, value in details.items():
                print(f"    {key:<12} | {value}")

def main():
    books = create_book_details()

    print(f"\nCreated {len(books)} books.")


if __name__ == "__main__":
    main()