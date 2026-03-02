import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    ChatJoinRequest,
)
import database as db

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))
DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

app = Client(
    "desi_mlh_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def get_default_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📺 Get Video", callback_data="get_video"),
            InlineKeyboardButton("👤 My Status", callback_data="my_status"),
        ],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer_link")],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/your_channel"),
            InlineKeyboardButton("🛠 Support", url="https://t.me/IH_Maruf"),
        ]
    ])

async def send_log(c, message):
    try:
        await app.send_message(LOG_GROUP_ID, message)
    except Exception as e:
        print(f"Error sending log: {e}")

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    referred_by = None
    if len(message.command) > 1:
        try:
            referred_by = int(message.command[1])
            if referred_by == user_id: referred_by = None
        except ValueError:
            referred_by = None

    is_new_user = await db.add_user(user_id, first_name, username, referred_by)
    
    if is_new_user:
        await send_log(f"👤 New User:\nName: {first_name}\nID: {user_id}\nUsername: @{username}")
        if referred_by:
            inviter = await db.get_user(referred_by)
            if inviter:
                await db.update_user(referred_by, {
                    "ref_count": inviter["ref_count"] + 1,
                    "daily_limit": inviter["daily_limit"] + 5
                })
                try:
                    await client.send_message(referred_by, "🎉 অভিনন্দন! আপনার রেফারেল লিঙ্কের মাধ্যমে একজন নতুন সদস্য যোগ দিয়েছেন। আপনার ডেইলি ভিডিও লিমিট +5 বাড়ানো হয়েছে।")
                except: pass

    welcome_text = """
━━━━━━━━━━━━━━━━━━━
✨🎬  𝑾𝑬𝑳𝑪𝑶𝑴𝑬 𝑻𝑶 𝑫𝑬𝑺𝑰 𝑴𝑳𝑯  🎬✨
━━━━━━━━━━━━━━━━━━━
🌟 হ্যালো & আসসালামু আলাইকুম 🌟
💎 অভিনন্দন! আপনি এখন 𝑫𝑬𝑺𝑰 𝑴𝑳𝑯 ভিডিও পরিবারের একজন সদস্য।
🎥 এখানে নিয়মিত এক্সক্লুসিভ ভিডিও শেয়ার করা হয়।
ভিডিও দেখতে নিচের কমান্ড ব্যবহার করুন —
👉 🔥 /video 🔥
━━━━━━━━━━━━━━━━━━━
📜 𝗚𝗥𝗢𝗨𝗣 𝗥𝗨𝗟𝗘𝗦
━━━━━━━━━━━━━━━━━━━
✅ ভদ্রতা বজায় রাখুন
✅ স্প্যাম বা অপ্রাসঙ্গিক মেসেজ নয়
✅ অশালীন কনটেন্ট সম্পূর্ণ নিষিদ্ধ
⚠️ নিয়ম ভঙ্গ করলে বিনা নোটিশে রিমুভ করা হবে।
━━━━━━━━━━━━━━━━━━━
💖 ধন্যবাদ আমাদের সাথে থাকার জন্য!
— 🤖 𝑫𝑬𝑺𝑰 𝑴𝑳𝑯 𝑩𝒐𝒕
━━━━━━━━━━━━━━━━━━━
"""
    await message.reply_text(welcome_text, reply_markup=get_default_buttons())

@app.on_chat_join_request()
async def auto_approve_join_request(client, join_request):
    try:
        await client.approve_chat_join_request(join_request.chat.id, join_request.from_user.id)
        await db.add_user(join_request.from_user.id, join_request.from_user.first_name, join_request.from_user.username)
        await send_log(f"✅ Approved & Saved:\nName: {join_request.from_user.first_name}\nID: {join_request.from_user.id}")
    except Exception as e:
        await send_log(f"Error approving join request: {e}")

@app.on_message(filters.chat(DATABASE_CHANNEL_ID) & filters.video)
async def new_video_handler(client, message):
    if message.video:
        await db.add_video(message.video.file_id)
        await send_log(f"📹 New video added: {message.video.file_id}")

@app.on_callback_query()
async def callback_handler(client, query):
    user_id = query.from_user.id
    user = await db.get_user(user_id)

    if user and datetime.now() - user['last_reset'] > timedelta(days=1):
        await db.update_user(user_id, {"today_used": 0, "last_reset": datetime.now()})
        user = await db.get_user(user_id)

    if query.data == "get_video":
        if user['today_used'] < user['daily_limit']:
            video_id = await db.get_random_video()
            if video_id:
                try:
                    await query.message.reply_video(video_id, caption="🎬 Here is your video!", reply_markup=get_default_buttons())
                    await db.update_user(user_id, {"today_used": user['today_used'] + 1})
                except Exception:
                    await query.answer("ভিডিও পাঠাতে সমস্যা হয়েছে।", show_alert=True)
            else:
                await query.answer("কোনো ভিডিও পাওয়া যায়নি।", show_alert=True)
        else:
            await query.answer(f"আজকের লিমিট শেষ! আপনার মোট লিমিট: {user['daily_limit']}", show_alert=True)
        await query.answer()

    elif query.data == "my_status":
        await my_status_command(client, query.message)
    
    elif query.data == "refer_link":
        bot_username = (await client.get_me()).username
        refer_link = f"https://t.me/{bot_username}?start={user_id}"
        await query.message.reply_text(f"🔗 আপনার রেফারেল লিঙ্ক:\n`{refer_link}`\n\nপ্রতিটি সফল রেফারে ডেইলি ভিডিও লিমিট +5 বাড়বে!", reply_markup=get_default_buttons())
        await query.answer()

@app.on_message(filters.command("status") & filters.private)
async def my_status_command(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user: return await message.reply_text("ব্যবহারকারী পাওয়া যায়নি।")
    
    status_text = f"""
━━━━━━━━━━━━━━━━━━━
📊 𝗨𝗦𝗘𝗥 𝗥𝗘𝗣𝗢𝗥𝗧
━━━━━━━━━━━━━━━━━━━
👤 Name: {user['first_name']}
🆔 ID: {user['user_id']}
👥 Referrals: {user['ref_count']}
🔹 Today: {user['today_used']}/{user['daily_limit']}
━━━━━━━━━━━━━━━━━━━
"""
    await message.reply_text(status_text, reply_markup=get_default_buttons())

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_command(client, message):
    if not message.reply_to_message: return await message.reply("মেসেজে রিপ্লাই দিন।")
    
    all_users = await db.get_all_users()
    success = 0
    async for user in all_users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            success += 1
            await asyncio.sleep(0.05)
        except: pass
    await message.reply(f"✅ ব্রডকাস্ট শেষ। সফলভাবে {success} জনের কাছে পৌঁছেছে।")

async def main():
    await app.start()
    print("Bot is running...")
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
