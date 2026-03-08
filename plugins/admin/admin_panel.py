from pyrogram import Client, filters
from config import ADMIN_IDS

from messages.admin.admin_panel_msg import admin_panel_message
from buttons.admin.admin_panel_buttons import admin_panel_buttons


@Client.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
async def admin_panel(client, message):

    text = admin_panel_message()
    buttons = admin_panel_buttons()

    await message.reply(
        text,
        reply_markup=buttons
    )