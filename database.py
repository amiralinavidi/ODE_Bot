# database.py
import sqlite3

DB_NAME = "ode_class.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # NEW SCHEMA: Centered around SID and Telegram Username
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            telegram_username TEXT UNIQUE, 
            numeric_id INTEGER UNIQUE,     
            text_score INTEGER DEFAULT 0,
            photo_score INTEGER DEFAULT 0,
            file_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0
        )
    ''')
    
    # A separate table for unknown users (people not in your roster)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unknown_users (
            numeric_id INTEGER PRIMARY KEY,
            telegram_username TEXT,
            first_name TEXT,
            total_score INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("New database initialized with roster support.")

def add_points(username, numeric_id, first_name, msg_type):
    """Matches the user and adds points."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Strip the '@' from the username just in case
    clean_username = username.replace('@', '').lower() if username else None

    # Step 1: Try to find them in the official roster by username OR numeric_id
    cursor.execute('''
        SELECT student_id FROM users 
        WHERE telegram_username = ? OR numeric_id = ?
    ''', (clean_username, numeric_id))
    
    student = cursor.fetchone()
    
    if student:
        sid = student[0]
        # Lock in their numeric_id if we haven't already
        cursor.execute('UPDATE users SET numeric_id = ? WHERE student_id = ?', (numeric_id, sid))
        
        # Add points to the official roster
        if msg_type == 'file':
            cursor.execute('UPDATE users SET file_score = file_score + 1, total_score = total_score + 3 WHERE student_id = ?', (sid,))
        elif msg_type == 'photo':
            cursor.execute('UPDATE users SET photo_score = photo_score + 1, total_score = total_score + 2 WHERE student_id = ?', (sid,))
        elif msg_type == 'text':
            cursor.execute('UPDATE users SET text_score = text_score + 1, total_score = total_score + 1 WHERE student_id = ?', (sid,))
    else:
        # Step 2: If they aren't in the roster, log them in unknown_users
        cursor.execute('''
            INSERT OR IGNORE INTO unknown_users (numeric_id, telegram_username, first_name) 
            VALUES (?, ?, ?)
        ''', (numeric_id, clean_username, first_name))
        
        if msg_type in ['file', 'photo', 'text']:
            points = 3 if msg_type == 'file' else 2 if msg_type == 'photo' else 1
            cursor.execute('UPDATE unknown_users SET total_score = total_score + ? WHERE numeric_id = ?', (points, numeric_id))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()