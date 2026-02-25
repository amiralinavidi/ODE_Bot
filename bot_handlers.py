import telebot
import re
from config import BOT_TOKEN, ADMIN_ID, ODE_GROUP_ID
from database import add_points # Import your new database function

bot = telebot.TeleBot(BOT_TOKEN)

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
        bot.reply_to(message, "⚙️ Welcome to the Admin Panel.\n\nDatabase is currently tracking group messages silently.")
    else:
        bot.reply_to(message, "You are not an administrator.")

# ==========================================
# GROUP TRACKER - STRICTLY ODE GROUP
# ==========================================
@bot.message_handler(content_types=['text', 'photo', 'document', 'video', 'voice', 'audio'], func=lambda message: message.chat.type in ['group', 'supergroup'])
def track_activity(message):
    # Ensure we only track the specific class group
    if message.chat.id != ODE_GROUP_ID:
        return
        
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    # Get the text username (returns None if they don't have one)
    telegram_username = message.from_user.username 
    
    # Ignore admin messages
    if user_id == ADMIN_ID:
        return

    content_type = message.content_type
    
    # Handle Files (+3)
    if content_type in ['document', 'video', 'voice', 'audio']:
        add_points(telegram_username, user_id, user_name, 'file')
        print(f"[DB] +3 points for file.")
        
    # Handle Photos (+2)
    elif content_type == 'photo':
        add_points(telegram_username, user_id, user_name, 'photo')
        print(f"[DB] +2 points for photo.")
        
    # Handle Text (+1 with Junk Filter)
    elif content_type == 'text':
        raw_text = message.text
        clean_text = re.sub(r'[^\w\s]', '', raw_text).strip().lower()
        
        is_valid_content = (len(clean_text) > 2 and clean_text not in STOP_WORDS) or clean_text.isdigit()
        
        if is_valid_content:
            add_points(telegram_username, user_id, user_name, 'text')
            print(f"[DB] +1 point for valid text.")