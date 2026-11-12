import json
import random
import string
from datetime import datetime
from pathlib import Path

DATABASE = Path("library.json")
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ------------------- Input helpers ------------------- #
def ask_int(prompt, min_value=None):
    """Keep asking until the user enters a whole number (optionally >= min_value)."""
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Please enter numbers only.")
            continue
        if min_value is not None and value < min_value:
            print(f"Please enter a number that is {min_value} or higher.")
            continue
        return value


def ask_text(prompt):
    """Keep asking until the user enters a non-empty string."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def valid_email(email):
    local, _, domain = email.partition("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


# ------------------- Library ------------------- #
class Library:
    def __init__(self):
        self.data = self.load_data()

    # ---------- Storage ---------- #
    @staticmethod
    def load_data():
        """Load library.json. A missing or empty file means a fresh library."""
        if not DATABASE.exists() or DATABASE.stat().st_size == 0:
            return {"books": [], "members": []}
        try:
            data = json.loads(DATABASE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            raise SystemExit(f"{DATABASE} is corrupted ({err}). Fix or delete it and try again.")
        data.setdefault("books", [])
        data.setdefault("members", [])
        return data

    def save_data(self):
        DATABASE.write_text(json.dumps(self.data, indent=4), encoding="utf-8")

    # ---------- Helpers ---------- #
    def generate_id(self, prefix="B"):
        """Generate an ID that is not already used by any book or member."""
        existing = {item["id"] for item in self.data["books"] + self.data["members"]}
        while True:
            random_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
            new_id = f"{prefix}-{random_id}"
            if new_id not in existing:
                return new_id

    def _find_member(self):
        member_id = input("Enter your library Id --> ").strip().upper()
        member = next((m for m in self.data["members"] if m["id"] == member_id), None)
        if member is None:
            print("No such member ID exists.")
        return member

    def _find_book(self):
        book_id = input("Enter the book Id --> ").strip().upper()
        book = next((b for b in self.data["books"] if b["id"] == book_id), None)
        if book is None:
            print("No such book exists.")
        return book

    # ---------- Books ---------- #
    def add_book(self):
        title = ask_text("Enter book title --> ")
        author = ask_text("Enter the book author --> ")
        copies = ask_int("How many copies --> ", min_value=1)

        book = {
            "id": self.generate_id("B"),
            "title": title,
            "author": author,
            "total_copies": copies,
            "available_copies": copies,
            "added_on": datetime.now().strftime(DATE_FORMAT),
        }
        self.data["books"].append(book)
        self.save_data()
        print(f"Book added successfully! ID: {book['id']}")

    def list_books(self):
        if not self.data["books"]:
            print("No books found.")
            return
        print(f"{'ID':12} {'Title':25} {'Author':20} Available/Total")
        print("-" * 70)
        for b in self.data["books"]:
            print(
                f"{b['id']:12} {b['title'][:24]:25} {b['author'][:19]:20} "
                f"{b['available_copies']}/{b['total_copies']}"
            )

    # ---------- Members ---------- #
    def add_member(self):
        name = ask_text("Enter your name --> ")
        while True:
            email = ask_text("Enter your email --> ")
            if not valid_email(email):
                print("That doesn't look like a valid email.")
            elif any(m["email"].lower() == email.lower() for m in self.data["members"]):
                print("A member with this email already exists.")
            else:
                break

        member = {
            "id": self.generate_id("M"),
            "name": name,
            "email": email,
            "borrowed": [],
        }
        self.data["members"].append(member)
        self.save_data()
        print(f"Member added successfully! ID: {member['id']}")

    def list_members(self):
        if not self.data["members"]:
            print("There are no members.")
            return
        print(f"{'ID':12} {'Name':25} Email")
        print("-" * 70)
        for m in self.data["members"]:
            print(f"{m['id']:12} {m['name'][:24]:25} {m['email']}")
            if m["borrowed"]:
                print("    Currently borrowed:")
                for entry in m["borrowed"]:
                    print(f"      - {entry['title']} ({entry['book_id']}) on {entry['borrow_on']}")
            else:
                print("    Currently borrowed: none")

    # ---------- Borrow / Return ---------- #
    def borrow(self):
        member = self._find_member()
        if member is None:
            return
        book = self._find_book()
        if book is None:
            return

        if book["available_copies"] <= 0:
            print("Sorry, the book is out of stock.")
            return
        if any(entry["book_id"] == book["id"] for entry in member["borrowed"]):
            print("You have already borrowed this book.")
            return

        member["borrowed"].append({
            "book_id": book["id"],
            "title": book["title"],
            "borrow_on": datetime.now().strftime(DATE_FORMAT),
        })
        book["available_copies"] -= 1
        self.save_data()
        print(f"'{book['title']}' borrowed successfully!")

    def return_book(self):
        member = self._find_member()
        if member is None:
            return
        if not member["borrowed"]:
            print("No books borrowed.")
            return

        print("-" * 20 + " Borrowed book list " + "-" * 20)
        for i, b in enumerate(member["borrowed"], start=1):
            print(f"{i}. {b['title']} ({b['book_id']})")

        choice = ask_int("Enter number to return (0 to cancel) --> ", min_value=0)
        if choice == 0:
            return
        if choice > len(member["borrowed"]):
            print("Invalid number.")
            return

        selected = member["borrowed"].pop(choice - 1)
        book = next((b for b in self.data["books"] if b["id"] == selected["book_id"]), None)
        if book:
            book["available_copies"] += 1
        self.save_data()
        print(f"'{selected['title']}' returned successfully!")


def main():
    library = Library()
    actions = {
        1: library.add_book,
        2: library.list_books,
        3: library.add_member,
        4: library.list_members,
        5: library.borrow,
        6: library.return_book,
    }

    while True:
        print("=" * 50)
        print(" LIBRARY MANAGEMENT SYSTEM ")
        print("=" * 50)
        print("    1. Add book")
        print("    2. List books")
        print("    3. Add member")
        print("    4. List members")
        print("    5. Borrow book")
        print("    6. Return book")
        print("    7. Exit")
        print("=" * 50)

        choice = ask_int("What task do you want to do --> ")
        if choice == 7:
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option. Please choose a number from 1 to 7.")


if __name__ == "__main__":
    main()
