from datetime import datetime
from database import users


async def reset_daily():
    today = str(datetime.utcnow().date())

    async for user in users.find():
        if user.get("last_reset_date") != today:
            await users.update_one(
                {"user_id": user["user_id"]},
                {
                    "$set": {
                        "today_video_used": 0,
                        "last_reset_date": today
                    }
                }
            )
