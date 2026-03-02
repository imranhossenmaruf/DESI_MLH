import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

ADMIN_IDS = []
if os.environ.get("ADMIN_IDS"):
    ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS").split(",")))

LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID", 0))
