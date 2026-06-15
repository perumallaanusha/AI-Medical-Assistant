import sqlite3


def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    # ---------------- Users Table ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # ---------------- Prediction History Table ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        symptoms TEXT,
        disease TEXT,
        confidence REAL,
        date_time TEXT
    )
    """)

    conn.commit()

    conn.close()


if __name__ == "__main__":

    init_db()

    print("Database Created Successfully!")