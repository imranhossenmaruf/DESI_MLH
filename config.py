import os
from dotenv import load_dotenv

load_dotenv() # .env ফাইল থেকে ডাটা লোড করার জন্য

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID", "0"))
MONGO_URL = os.getenv("MONGO_URL")
