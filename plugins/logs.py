from pyrogram import Client, filters
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

# ডেটাবেস কানেকশন
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.video_bot_db
user_collection = db.users

# তোর লগ গ্রুপের আইডি
LOG_GROUP_ID = -1003744642897 

@Client.on_chat_join_request()
async def join_log_handler(client, message):
    chat = message.chat
    user = message.from_user
    
    # ১. ডেটাবেসে ইউজার সেভ করা (ইউজার সংখ্যা বাড়াতে এটি দরকার)
    if not await user_collection.find_one({"user_id": user.id}):
        await user_collection.insert_one({
            "user_id": user.id,
            "type": "private",
            "is_blocked": False,
            "join_date": datetime.now(),
            "refers": 0,
            "watched_today": 0
        })

    # ২. জয়েন রিকোয়েস্ট এপ্রুভ করা
    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    except Exception as e:
        print(f"Approve Error: {e}")

    # ৩. তোর কাছে লগ মেসেজ পাঠানো
    log_text = (
        "📢 **Auto Approval Log**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **User:** {user.first_name}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"👥 **Group:** {chat.title}\n"
        f"📅 **Time:** {datetime.now().strftime('%I:%M %p')}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "✅ **Status:** Saved & Approved"
    )

    try:
        await client.send_message(chat_id=LOG_GROUP_ID, text=log_text)
    except Exception as e:
        print(f"Log Error: {e}")
