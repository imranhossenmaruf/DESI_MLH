import random
import asyncio
from datetime import datetime
from pyrogram import filters
from database import add_user, get_user, increment_user, videos
from utils.referral import process_referral
from config import LOG_GROUP_ID


async def register_user(app):

    @app.on_message(filters.command("start"))
    async def start(_, message):
        args = message.text.split()

        user_data = {
            "user_id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "join_date": datetime.utcnow(),
            "referred_by": None,
            "referral_count": 0,
            "daily_video_limit": 5,
            "today_video_used": 0,
            "last_reset_date": str(datetime.utcnow().date())
        }

        await add_user(user_data)

        if len(args) > 1:
            try:
                await process_referral(message.from_user.id, int(args[1]))
            except:
                pass

        await message.reply_text(
            f"<b>👋 Welcome {message.from_user.first_name}!</b>\n\nUse /video to watch.",
            parse_mode="html"
        )

    @app.on_message(filters.command("video"))
    async def send_video(_, message):
        user = await get_user(message.from_user.id)

        if user["today_video_used"] >= user["daily_video_limit"]:
            return await message.reply_text("<b>Daily limit reached!</b>", parse_mode="html")

        video_list = [v async for v in videos.find()]
        if not video_list:
            return await message.reply_text("No videos available.")

        video = random.choice(video_list)
        sent = await message.reply_video(video["file_id"])

        await increment_user(message.from_user.id, "today_video_used", 1)

        await asyncio.sleep(600)
        await sent.delete()
