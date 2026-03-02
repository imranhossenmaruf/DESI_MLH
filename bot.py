import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from handlers.user import register_user
from handlers.admin import admin_panel
from handlers.security import security
from utils.reset_daily import reset_daily

logging.basicConfig(level=logging.INFO)

app = Client(
    "VideoReferralBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


async def main():
    await register_user(app)
    await admin_panel(app)
    await security(app)
    await reset_daily()


app.run(main())
