import telebot
import re
from config import BOT_TOKEN, ADMIN_ID, ODE_GROUP_ID
from database import add_points # Import your new database function
import pandas as pd
import sqlite3
import os

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Junk filter from your original script
STOP_WORDS = {
    'سلام', 'درود', 'ممنون', 'مرسی', 'تشکر', 'سپاس', 'بله', 'خیر', 'نه',
    'ok', 'thanks', 'hi', 'hello', 'استاد', 'بچه ها', 'خداحافظ', 'فعلا',
    'اره', 'آره', 'دقیقا', 'درسته', 'چشم', 'merci'
}

# ==========================================
# ADMIN PANEL - STRICTLY PRIVATE MESSAGES (PV)
# ==========================================
@bot.message_handler(commands=['admin', 'start'], func=lambda message: message.chat.type == 'private')
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "⚙️ Welcome to the Admin Panel.\n\nCommands:\n/export - Download the latest grade Excel sheet")
    else:
        bot.reply_to(message, "You are not an administrator.")

@bot.message_handler(commands=['export'], func=lambda message: message.chat.type == 'private')
def handle_export(message):
    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(message, "⏳ Generating the latest ODE Grade Report...")

    try:
        # 1. Connect to the database
        db_path = '/home/AmiraliNotFound/ODE_Bot/ode_class.db'
        conn = sqlite3.connect(db_path)

        # 2. Pull the data into Pandas DataFrames, sorted by highest score
        df_users = pd.read_sql_query("SELECT * FROM users ORDER BY total_score DESC", conn)
        df_unknown = pd.read_sql_query("SELECT * FROM unknown_users ORDER BY total_score DESC", conn)
        conn.close()

        # 3. Create the Excel file
        excel_path = '/home/AmiraliNotFound/ODE_Bot/ODE_Class_Grades.xlsx'
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_users.to_excel(writer, sheet_name='Students (SID)', index=False)
            df_unknown.to_excel(writer, sheet_name='Unknown Users', index=False)

        # 4. Send the file back to you on Telegram
        with open(excel_path, 'rb') as doc:
            bot.send_document(message.chat.id, doc, caption="📊 Here is the latest activity report!")

    except Exception as e:
        bot.reply_to(message, f"❌ Error generating report: {e}")

# ==========================================
# GROUP TRACKER - STRICTLY ODE GROUP
# ==========================================
@bot.message_handler(content_types=['text', 'photo', 'document', 'video', 'voice', 'audio'], func=lambda message: message.chat.type in ['group', 'supergroup'])
def track_activity(message):

    print(f"🚨 DEBUG [1]: Message caught! Chat ID: {message.chat.id} | User ID: {message.from_user.id} | Type: {message.content_type}", flush=True)

    # 1. Check Group ID
    if message.chat.id != ODE_GROUP_ID:
        print(f"❌ DEBUG [2]: IGNORING. Chat ID {message.chat.id} does not match your .env ODE_GROUP_ID {ODE_GROUP_ID}", flush=True)
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    telegram_username = message.from_user.username

    # 2. Check Admin Status
    if user_id == ADMIN_ID:
        print("❌ DEBUG [3]: IGNORING. User is the Admin.", flush=True)
        return

    content_type = message.content_type
    print(f"✅ DEBUG [4]: Passed ID checks! Processing {content_type}...", flush=True)

    # 3. Handle Files
    if content_type in ['document', 'video', 'voice', 'audio']:
        print(f"💾 DEBUG [5]: Sending FILE points to database...", flush=True)
        add_points(telegram_username, user_id, user_name, 'file')

    # 4. Handle Photos
    elif content_type == 'photo':
        print(f"💾 DEBUG [5]: Sending PHOTO points to database...", flush=True)
        add_points(telegram_username, user_id, user_name, 'photo')

    # 5. Handle Text
    elif content_type == 'text':
        raw_text = message.text
        clean_text = re.sub(r'[^\w\s]', '', raw_text).strip().lower()
        print(f"📝 DEBUG [5]: Cleaned text is -> '{clean_text}'", flush=True)

        is_valid_content = (len(clean_text) > 2 and clean_text not in STOP_WORDS) or clean_text.isdigit()

        if is_valid_content:
            print(f"💾 DEBUG [6]: Text is VALID! Sending TEXT points to database...", flush=True)
            add_points(telegram_username, user_id, user_name, 'text')
        else:
            print(f"⚠️ DEBUG [6]: Text is INVALID (too short or stop-word). Tossed in trash.", flush=True)