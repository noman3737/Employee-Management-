import sqlite3

# ---------- CREATE CONNECTION ----------
def create_connection():
    conn = sqlite3.connect("employee.db", check_same_thread=False)
    return conn


# ---------- CREATE EMPLOYEE TABLE ----------
def create_table():
    conn = create_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            department TEXT,
            designation TEXT,
            salary REAL,
            joining_date TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------- CREATE USER TABLE ----------
def create_user_table():
    conn = create_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    # Insert default admin if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "Admin")
        )

    conn.commit()
    conn.close()
