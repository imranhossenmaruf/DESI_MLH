from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, LOG_GROUP_ID

app = Client(
    "mybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Welcome to My Bot!\n\nBot is running successfully ✅"
    )

@app.on_message(filters.command("admin"))
async def admin_check(client, message):
    if message.from_user.id in ADMIN_IDS:
        await message.reply_text("✅ You are Admin")
    else:
        await message.reply_text("❌ You are not Admin")

print("Bot Started...")
app.run()
