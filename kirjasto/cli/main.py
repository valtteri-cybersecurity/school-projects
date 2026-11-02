from cli.create import create_book_details
from cli.actions import (
    save_books,
    list_books,
    search_by_name,
    search_by_author
)
from cli.ui import (
    clear_screen,
    main_menu,
    main_menu_navigation
)

def main():
    while True:
        main_menu()
        choice = main_menu_navigation()

        if choice == 5:
            print("Program closing down...")
            break

        elif choice == 1:
            clear_screen()
            books = create_book_details()

            if not books:
                print("No books to save!")
                continue

            try:
                save_books(books)
                print("Books saved in book register!")
            except (ValueError, OSError) as e:
                print(f"Unable to save books: {e}")

        elif choice == 2:
            clear_screen()

            try:
                list_books()
            except (ValueError, OSError) as e:
                print(f"Unable to list books: {e}")

        elif choice == 3:
            clear_screen()

            try:
                search_by_name()
            except (ValueError, OSError) as e:
                print(f"Unable to search books: {e}")

        elif choice == 4:
            clear_screen()

            try:
                search_by_author()
            except (ValueError, OSError) as e:
                print(f"Unable to search authors: {e}")

if __name__ == "__main__":
    main()