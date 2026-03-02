from pyrogram import filters
from config import ADMIN_IDS
from database import users

admin_mode = {}


async def admin_panel(app):

    @app.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
    async def toggle(_, message):
        admin_mode[message.from_user.id] = not admin_mode.get(message.from_user.id, False)
        await message.reply_text("Admin mode toggled.")

    @app.on_message(filters.user(ADMIN_IDS))
    async def broadcast(_, message):
        if not admin_mode.get(message.from_user.id):
            return

        success = 0
        failed = 0

        async for user in users.find():
            try:
                await message.copy(user["user_id"])
                success += 1
            except:
                failed += 1

        await message.reply_text(f"Done\nSuccess: {success}\nFailed: {failed}")
