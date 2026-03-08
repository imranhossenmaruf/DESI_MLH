from pyrogram import Client, filters
from config import ADMIN_IDS
from systems.broadcast import broadcast_message


@Client.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast(client, message):

    if len(message.command) < 2:
        return await message.reply("Usage:\n/broadcast message")

    text = message.text.split(None, 1)[1]

    await broadcast_message(client, text)

    await message.reply("📢 Broadcast Sent")