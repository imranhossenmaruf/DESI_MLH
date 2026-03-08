from pyrogram import Client, filters
from systems.premium import check_premium


@Client.on_message(filters.command("premium"))
async def premium_command(client, message):

    user_id = message.from_user.id

    status = await check_premium(user_id)

    if status:
        text = "💎 You are a Premium User"
    else:
        text = "❌ You don't have Premium"

    await message.reply(text)