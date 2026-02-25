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

def add_points(telegram_id, name, msg_type):
    """Adds points to a user based on message type."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Ensure the user exists in the database (INSERT OR IGNORE)
    cursor.execute('''
        INSERT OR IGNORE INTO users (telegram_id, name) 
        VALUES (?, ?)
    ''', (telegram_id, name))
    
    # 2. Always update their latest Telegram name just in case they changed it
    cursor.execute('''
        UPDATE users SET name = ? WHERE telegram_id = ?
    ''', (name, telegram_id))
    
    # 3. Add the points
    if msg_type == 'file':
        cursor.execute('''
            UPDATE users SET file_score = file_score + 1, total_score = total_score + 3 
            WHERE telegram_id = ?
        ''', (telegram_id,))
    elif msg_type == 'photo':
        cursor.execute('''
            UPDATE users SET photo_score = photo_score + 1, total_score = total_score + 2 
            WHERE telegram_id = ?
        ''', (telegram_id,))
    elif msg_type == 'text':
        cursor.execute('''
            UPDATE users SET text_score = text_score + 1, total_score = total_score + 1 
            WHERE telegram_id = ?
        ''', (telegram_id,))
        
    conn.commit()
    conn.close()