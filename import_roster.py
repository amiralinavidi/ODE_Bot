# import_roster.py
import sqlite3
import pandas as pd
import os

# Force absolute paths for PythonAnywhere!
DB_NAME = "" # Set this to your database file name (e.g., 'ode_class.db')
ROSTER_FILE = ""  # Set this to your roster file name (e.g., 'roster.xlsx' or 'roster.csv')

def import_roster(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find '{file_path}'. Please ensure it is in the same folder.")
        return

    print(f"📄 Reading {file_path}...")
    
    # Load the file depending on its extension
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        # Note: You might need to run `pip install openpyxl` if you haven't already
        df = pd.read_excel(file_path)

    # Check if the required columns exist
    required_columns = ['Student_ID', 'Name', 'Telegram_Username']
    for col in required_columns:
        if col not in df.columns:
            print(f"❌ Error: Your file is missing the '{col}' column.")
            return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    success_count = 0
    
    for index, row in df.iterrows():
        # Clean the Student ID (convert to string, remove decimals if Excel made it a float)
        sid = str(row['Student_ID']).split('.')[0].strip()
        name = str(row['Name']).strip()
        
        # Clean the Telegram Username (remove @, make lowercase, handle empty cells)
        username = str(row['Telegram_Username']).strip()
        if username.lower() == 'nan' or not username:
            username = None
        else:
            username = username.replace('@', '').lower()

        try:
            # INSERT OR REPLACE ensures that if you run this script twice, 
            # it updates existing students instead of creating duplicates.
            cursor.execute('''
                INSERT OR REPLACE INTO users (student_id, name, telegram_username)
                VALUES (?, ?, ?)
            ''', (sid, name, username))
            success_count += 1
        except Exception as e:
            print(f"⚠️ Failed to insert {name} ({sid}): {e}")

    conn.commit()
    conn.close()
    print(f"✅ Successfully imported {success_count} students into the database.")

if __name__ == '__main__':
    import_roster(ROSTER_FILE)