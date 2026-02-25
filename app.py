# app.py
from flask import Flask, request, abort
import telebot
from config import BOT_TOKEN, WEBHOOK_URL
from bot_handlers import bot

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot is running!", 200

# Webhook endpoint securely using the BOT_TOKEN in the URL
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

# Quick route to set the webhook to PythonAnywhere
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    success = bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    if success:
        return f"Webhook successfully set to {WEBHOOK_URL}/{BOT_TOKEN}", 200
    else:
        return "Webhook setup failed.", 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)