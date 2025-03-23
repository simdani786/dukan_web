import sqlite3

def init_db():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT NOT NULL,
            date TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            bus_number TEXT NOT NULL,
            total_amount REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
