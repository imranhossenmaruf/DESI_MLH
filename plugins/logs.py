import urllib.parse
from datetime import datetime
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, ADMIN_IDS
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ডাটাবেস কানেকশন
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.video_bot_db
user_collection = db.users

LOG_GROUP_ID = -1003744642897 

@Client.on_chat_join_request()
async def auto_approve_and_log(client, message):
    user = message.from_user
    chat = message.chat
    
    # ১. ডেটাবেসে ইউজার সেভ করা
    if not await user_collection.find_one({"user_id": user.id}):
        await user_collection.insert_one({
            "user_id": user.id,
            "type": "private",
            "is_blocked": False,
            "join_date": datetime.now(),
            "refers": 0,
            "watched_today": 0
        })

    # ২. রিকোয়েস্ট এপ্রুভ ও মেসেজ পাঠানো
    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        
        bot = await client.get_me()
        premium_msg = "Hello Admin 👋\nI would like to upgrade to Premium Membership."
        encoded_msg = urllib.parse.quote(premium_msg)

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ADD ME TO GROUP", url=f"https://t.me/{bot.username}?startgroup=true"),
             InlineKeyboardButton("🔞 VIP🫦", url="https://t.me/+1apgXrLWXuE4M2Y1")],
            [InlineKeyboardButton("👤 MY STATUS", callback_data="my_status"), 
             InlineKeyboardButton("💎 BUY PREMIUM", url=f"https://t.me/IH_Maruf?text={encoded_msg}")],
            [InlineKeyboardButton("📊 Referral Info", callback_data="ref_info")]
        ])

        welcome_text = (
            "━━━━━━━━━━━━━━━━━━━\n"
            "✅ **JOIN REQUEST APPROVED**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** {user.first_name}\n"
            f"🆔 **User ID:** `{user.id}`\n\n"
            f"🎉 Welcome to **{chat.title}**!\n"
            "🎬 Watch videos: /video\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        
        try:
            await client.send_message(chat_id=user.id, text=welcome_text, reply_markup=buttons)
        except:
            pass

        # ৩. লগ গ্রুপে তথ্য পাঠানো
        current_time = datetime.now().strftime("%I:%M %p")
        log_message = (
            "📢 **Auto Approval Log**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User:** {user.mention}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"👥 **Group:** {chat.title}\n"
            f"📅 **Time:** {current_time}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "✅ **Status:** User Saved to Database"
        )
        await client.send_message(chat_id=LOG_GROUP_ID, text=log_message)

    except Exception as e:
        print(f"Log Plugin Error: {e}")
