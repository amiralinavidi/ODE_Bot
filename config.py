# config.py
import os
from dotenv import load_dotenv

# Load variables from .env file (only needed for local testing)
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Convert to integers for Telegram ID checking
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
ODE_GROUP_ID = int(os.getenv('ODE_GROUP_ID', 0))