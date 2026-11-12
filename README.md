# 📚 Library Management System

A simple library management system built in Python with two interfaces:

- **`app.py`**: a web interface built with [Streamlit](https://streamlit.io/)
- **`main.py`**: a command-line (terminal) interface

Both versions read and write the same `library.json` file, so data added in one shows up in the other. Run both from the same folder.

---

## ✨ Features

- **Add Book**: title, author and number of copies
- **List Books**: see every book with its available and total copies
- **Add Member**: register a member with name and email
- **List Members**: see all members and the books each one currently has
- **Borrow Book**: lend a book to a member
- **Return Book**: take a book back and restore the available copy

### Rules and validation

- Book title, author, member name and email cannot be empty
- A book must have at least **1 copy**
- Email must look valid, and two members cannot share the same email
- A book that is **out of stock cannot be borrowed**
- A member cannot borrow the same book twice at the same time
- Book and member IDs are auto-generated and always unique (`B-XXXXX` for books, `M-XXXXX` for members)

---

## 🛠️ Tech Stack

- Python 3.8+
- Streamlit (web version only)
- JSON file for storage (`library.json`)
- Standard library: `json`, `random`, `string`, `datetime`, `pathlib`

---

## 📁 Project Structure

```
├── app.py            # Streamlit web application
├── main.py           # Command-line version
├── library.json      # Library data (created automatically on first save)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

**Web version (Streamlit):**

```bash
streamlit run app.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

**Command-line version:**

```bash
python main.py
```

The menu repeats until you choose **7. Exit**:

```
1. Add book
2. List books
3. Add member
4. List members
5. Borrow book
6. Return book
7. Exit
```

---

## 💾 Data Storage

Everything is stored in `library.json`:

```json
{
    "books": [
        {
            "id": "B-4K9QZ",
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "total_copies": 3,
            "available_copies": 2,
            "added_on": "2026-11-12 10:30:00"
        }
    ],
    "members": [
        {
            "id": "M-7XA21",
            "name": "John Doe",
            "email": "john@example.com",
            "borrowed": [
                {
                    "book_id": "B-4K9QZ",
                    "title": "Clean Code",
                    "borrow_on": "2026-11-12 10:35:00"
                }
            ]
        }
    ]
}

---

## ⚠️ Limitations

- JSON file storage is not safe for many users writing at the same time
- No due dates, fines or overdue tracking
- No way to edit or delete books and members
- No login: anyone using the app can borrow or return for any member

---

## 🔮 Future Improvements

- Due dates and late fees
- Edit and delete for books and members
- Search and filter books by title or author
- Replace JSON with SQLite
- Admin login for the web version

---

## 👤 Author

**Aditya Kumar**
B.Tech Student, LNCT
