import os
from dotenv import load_dotenv

# .env ফাইল থেকে ডাটা লোড করা
load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
# ADMIN_IDS কমা দিয়ে আলাদা করা থাকলে সেটি লিস্টে রুপান্তর
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i]
DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID", "0"))
MONGO_URL = os.getenv("MONGO_URL")
BOT_USERNAME = "@DesiMlh_bot"