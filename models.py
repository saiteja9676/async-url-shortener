import sqlite3

DB_NAME = "urls.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread = False, timeout = 10)
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    #enable WAL mode for better concurrent access
    cursor.execute("PRAGMA journal_mode = WAL")

    # create urls table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code VARCHAR(10) UNIQUE,
                original_url VARCHAR(255) NOT NULL,
                status VARCHAR(20)
        )
    """)
    conn.commit()
    conn.close()