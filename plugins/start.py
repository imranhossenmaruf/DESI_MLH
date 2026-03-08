from pyrogram import Client, filters
from messages.start.start_msg import start_message
from buttons.start.start_buttons import start_buttons


@Client.on_message(filters.command("start"))
async def start_command(client, message):

    text = start_message(message.from_user)
    buttons = start_buttons()

    await message.reply(
        text,
        reply_markup=buttons,
        parse_mode="html"
    )