from pyrogram import Client, filters
from config import ADMIN_IDS
from systems.admin import ban_user


@Client.on_message(filters.command("ban") & filters.user(ADMIN_IDS))
async def ban(client, message):

    if len(message.command) < 2:
        return await message.reply("Usage:\n/ban user_id")

    user_id = int(message.command[1])

    await ban_user(user_id)

    await message.reply("🚫 User Banned")