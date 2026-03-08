from pyrogram import Client, filters
from messages.profile.profile_msg import profile_message


@Client.on_message(filters.command("profile"))
async def profile_command(client, message):

    user = message.from_user

    text = profile_message(user)

    await message.reply(text)