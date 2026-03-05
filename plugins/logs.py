import urllib.parse
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ডাটাবেস কানেকশন
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.video_bot_db
user_collection = db.users

print("--- Logs Plugin Loaded Successfully ---")

LOG_GROUP_ID = -1003744642897 

@Client.on_chat_join_request()
async def auto_approve_and_log(client, message):
    user = message.from_user
    chat = message.chat
    
    print(f"New Join Request: {user.id} in {chat.title}") # লগে প্রিন্ট হবে

    # ১. ইউজার সেভ করা
    try:
        if not await user_collection.find_one({"user_id": user.id}):
            await user_collection.insert_one({
                "user_id": user.id,
                "type": "private",
                "is_blocked": False,
                "join_date": datetime.now(),
                "refers": 0,
                "watched_today": 0
            })
    except Exception as db_err:
        print(f"Database Error: {db_err}")

    # ২. এপ্রুভ ও লগ পাঠানো
    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        
        # লগ মেসেজ তৈরি
        current_time = datetime.now().strftime("%I:%M %p")
        log_message = (
            "📢 **Auto Approval Log**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User:** {user.mention}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"👥 **Group:** {chat.title}\n"
            f"📅 **Time:** {current_time}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "✅ **Status:** User Approved & Saved"
        )
        
        await client.send_message(chat_id=LOG_GROUP_ID, text=log_message)
        print("Success: Log sent to group!")

    except Exception as e:
        print(f"Final Log Error: {e}") # কোনো এরর থাকলে এখানে দেখাবে
