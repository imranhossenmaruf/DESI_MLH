from pyrogram import filters


async def security(app):

    @app.on_message(filters.group)
    async def check(_, message):
        if (
            "http" in (message.text or "")
            or "https" in (message.text or "")
            or "t.me" in (message.text or "")
            or message.forward_date
        ):
            await message.delete()
            warn = await message.reply_text("⚠️ Links not allowed.")
            await warn.delete(20)
