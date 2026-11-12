import json
import random
import string
from datetime import datetime
from pathlib import Path

import streamlit as st

# set_page_config must be the first Streamlit command
st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

DATABASE = Path("library.json")
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ------------------- File and Data Handling ------------------- #
def load_data():
    """Load library.json. A missing or empty file means a fresh library.
    Raises json.JSONDecodeError if the file is corrupted."""
    if not DATABASE.exists() or DATABASE.stat().st_size == 0:
        return {"books": [], "members": []}
    data = json.loads(DATABASE.read_text(encoding="utf-8"))
    data.setdefault("books", [])
    data.setdefault("members", [])
    return data


def save_data(data):
    DATABASE.write_text(json.dumps(data, indent=4), encoding="utf-8")


def generate_id(data, prefix="B"):
    """Generate an ID that is not already used by any book or member."""
    existing = {item["id"] for item in data["books"] + data["members"]}
    while True:
        random_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        new_id = f"{prefix}-{random_id}"
        if new_id not in existing:
            return new_id


def valid_email(email):
    local, _, domain = email.partition("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


def flash(message):
    """Show a success message after the page reloads, so lists refresh immediately."""
    st.session_state["flash"] = message
    st.rerun()


# Always read from the file (not session_state) so several browser tabs/users
# and the command-line version never overwrite each other with stale data.
try:
    data = load_data()
except json.JSONDecodeError:
    st.error("library.json is corrupted. Fix or delete the file and reload the app.")
    st.stop()

st.title("📚 Library Management System")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

menu = st.sidebar.radio(
    "Menu",
    ["Add Book", "Book List", "Add Member", "Member List", "Borrow Book", "Return Book"],
)

# ---------------- Add Book ----------------
if menu == "Add Book":
    st.subheader("Add a New Book")
    with st.form("add_book_form", clear_on_submit=True):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        copies = st.number_input("Number of Copies", min_value=1, step=1)
        submitted = st.form_submit_button("Add Book")

    if submitted:
        if not title.strip() or not author.strip():
            st.error("Title and Author are required.")
        else:
            book = {
                "id": generate_id(data, "B"),
                "title": title.strip(),
                "author": author.strip(),
                "total_copies": int(copies),
                "available_copies": int(copies),
                "added_on": datetime.now().strftime(DATE_FORMAT),
            }
            data["books"].append(book)
            save_data(data)
            st.success(f"Book added successfully! ID: {book['id']}")

# ---------------- Book List ----------------
elif menu == "Book List":
    st.subheader("All Books")
    if not data["books"]:
        st.info("No books found.")
    else:
        st.dataframe(data["books"], hide_index=True)

# ---------------- Add Member ----------------
elif menu == "Add Member":
    st.subheader("Add a New Member")
    with st.form("add_member_form", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Add Member")

    if submitted:
        if not name.strip() or not email.strip():
            st.error("Name and Email are required.")
        elif not valid_email(email.strip()):
            st.error("Please enter a valid email address.")
        elif any(m["email"].lower() == email.strip().lower() for m in data["members"]):
            st.error("A member with this email already exists.")
        else:
            member = {
                "id": generate_id(data, "M"),
                "name": name.strip(),
                "email": email.strip(),
                "borrowed": [],
            }
            data["members"].append(member)
            save_data(data)
            st.success(f"Member added successfully! ID: {member['id']}")

# ---------------- Member List ----------------
elif menu == "Member List":
    st.subheader("All Members")
    if not data["members"]:
        st.info("No members found.")
    else:
        for m in data["members"]:
            with st.expander(f"{m['name']} ({m['id']}) - {m['email']}"):
                if m["borrowed"]:
                    st.write("Borrowed Books:")
                    st.table(m["borrowed"])
                else:
                    st.write("No books borrowed.")

# ---------------- Borrow Book ----------------
elif menu == "Borrow Book":
    st.subheader("Borrow a Book")
    if not data["members"] or not data["books"]:
        st.warning("You need at least one member and one book to borrow.")
    else:
        members_by_id = {m["id"]: m for m in data["members"]}
        books_by_id = {b["id"]: b for b in data["books"]}

        member_id = st.selectbox(
            "Select Member",
            list(members_by_id),
            format_func=lambda i: f"{members_by_id[i]['name']} ({i})",
        )
        book_id = st.selectbox(
            "Select Book",
            list(books_by_id),
            format_func=lambda i: (
                f"{books_by_id[i]['title']} ({i}) - {books_by_id[i]['available_copies']} available"
            ),
        )

        if st.button("Borrow"):
            member = members_by_id[member_id]
            book = books_by_id[book_id]

            if book["available_copies"] <= 0:
                st.error("Sorry, this book is out of stock.")
            elif any(entry["book_id"] == book["id"] for entry in member["borrowed"]):
                st.error("This member has already borrowed this book.")
            else:
                member["borrowed"].append({
                    "book_id": book["id"],
                    "title": book["title"],
                    "borrow_on": datetime.now().strftime(DATE_FORMAT),
                })
                book["available_copies"] -= 1
                save_data(data)
                flash(f"'{book['title']}' borrowed by {member['name']} successfully!")

# ---------------- Return Book ----------------
elif menu == "Return Book":
    st.subheader("Return a Book")
    if not data["members"]:
        st.warning("No members found.")
    else:
        members_by_id = {m["id"]: m for m in data["members"]}
        member_id = st.selectbox(
            "Select Member",
            list(members_by_id),
            format_func=lambda i: f"{members_by_id[i]['name']} ({i})",
        )
        member = members_by_id[member_id]
        borrowed = member["borrowed"]

        if not borrowed:
            st.info("This member has no borrowed books.")
        else:
            idx = st.selectbox(
                "Select Book to Return",
                range(len(borrowed)),
                format_func=lambda i: (
                    f"{borrowed[i]['title']} ({borrowed[i]['book_id']}) - "
                    f"borrowed on {borrowed[i]['borrow_on']}"
                ),
            )

            if st.button("Return Book"):
                selected = borrowed.pop(idx)
                book = next((b for b in data["books"] if b["id"] == selected["book_id"]), None)
                if book:
                    book["available_copies"] += 1
                save_data(data)
                flash(f"'{selected['title']}' returned successfully!")

# To run: streamlit run app.py
