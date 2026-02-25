# bot_handlers.py
import telebot
from config import BOT_TOKEN, ADMIN_ID, ODE_GROUP_ID

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# ADMIN PANEL - STRICTLY PRIVATE MESSAGES (PV)
# ==========================================
@bot.message_handler(commands=['admin', 'start'], func=lambda message: message.chat.type == 'private')
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "⚙️ Welcome to the Admin Panel.\n\nReady for database commands.")
    else:
        bot.reply_to(message, "You are not an administrator.")

# ==========================================
# GROUP TRACKER - STRICTLY ODE GROUP
# ==========================================
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def track_activity(message):
    # Ensure we only track the specific class group
    if message.chat.id != ODE_GROUP_ID:
        return

    # Ignore admin messages so they don't skew the leaderboard
    if message.from_user.id == ADMIN_ID:
        return

    # Placeholder for the database logic you'll tell me about next
    print(f"Message received from {message.from_user.first_name}. Ready to count points!")