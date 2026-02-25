import sqlite3
import time

DB_NAME = "ode_class.db"

def init_db():
    """Creates the database and the users table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create the main table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            student_id TEXT,
            text_score INTEGER DEFAULT 0,
            photo_score INTEGER DEFAULT 0,
            file_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            last_msg_timestamp REAL DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# We can run this file directly to test it
if __name__ == '__main__':
    init_db()