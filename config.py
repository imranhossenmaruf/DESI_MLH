import os

def get_env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and not value:
        print(f"WARNING: {name} is missing!")
    return value
DATABASE_CHANNEL_ID = get_inv("DATABASE_CHANNEL_ID", "")
API_ID = int(get_env("API_ID", 0))
API_HASH = get_env("API_HASH", "")
BOT_TOKEN = get_env("BOT_TOKEN", "", required=True)
MONGO_URL = get_env("MONGO_URL", "")

# Admin IDs safe handling
ADMIN_IDS = []
admin_env = get_env("ADMIN_IDS", "")
if admin_env:
    try:
        ADMIN_IDS = list(map(int, admin_env.split(",")))
    except:
        ADMIN_IDS = []

# Log Group safe
try:
    LOG_GROUP_ID = int(get_env("LOG_GROUP_ID", 0))
except:
    LOG_GROUP_ID = 0
