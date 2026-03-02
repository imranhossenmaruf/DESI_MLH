import asyncio
import random
import re
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from pyrogram.errors import UserIsBlocked, InputUserDeactivated
from motor.motor_asyncio import AsyncIOMotorClient
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, DATABASE_CHANNEL_ID, MONGO_URL

# ডাটাবেস কানেকশন
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.video_bot_db
video_collection = db.videos
user_collection = db.users

# এডমিন মোড ট্র্যাক লিস্ট
ADMIN_MODE_USERS = []

app = Client(
    "mybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

# ১. ইউজার ডাটা সেভ এবং রেফারেল ট্র্যাকিং
@app.on_message(filters.private & ~filters.service)
async def save_user(client, message):
    user_id = message.from_user.id
    if not await user_collection.find_one({"user_id": user_id}):
        await user_collection.insert_one({
            "user_id": user_id,
            "is_blocked": False,
            "join_date": datetime.now(),
            "refers": 0,
            "watched_today": 0
        })
    message.continue_propagation()

# ২. স্টার্ট কমান্ড (আপনার দেওয়া ওয়েলকাম ফরম্যাটে)
@app.on_message(filters.command("start"))
async def start(client, message):
    first_name = message.from_user.first_name
    welcome_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "✨🎬  **𝑾𝑬𝑳𝑪𝑶𝑴𝑬 𝑻𝑶 𝑫𝑬𝑺𝑰 𝑴𝑳𝑯** 🎬✨\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👑 Welcome **{first_name}**! 👑\n"
        "You are now a member of **𝑫𝑬𝑺𝑰 𝑴𝑳𝑯** Video Community 🎥\n\n"
        "🔥 To watch videos, use the command:\n"
        "👉 /video\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📜 **𝗥𝗨𝗟𝗘𝗦**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "✅ Be respectful\n"
        "✅ No spam\n"
        "✅ No adult/illegal content\n"
        "✅ Follow admin rules\n"
        "⚠️ Rule violation = Instant remove\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🎬 Stay Active | Enjoy Watching\n"
        "— 🤖 **𝑫𝑬𝑺𝑰 𝑴𝑳𝑯 𝑩𝒐𝒕**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_text(welcome_text)

# ৩. প্রোফাইল কমান্ড
@app.on_message(filters.command("profile") & filters.private)
async def user_profile(client, message):
    user_id = message.from_user.id
    user_data = await user_collection.find_one({"user_id": user_id})
    today_watched = user_data.get("watched_today", 0)
    total_refers = user_data.get("refers", 0)
    limit = 10
    
    profile_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "👤 **PROFILE - 𝑫𝑬𝑺𝑰 𝑴𝑳𝑯**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** {user_id}\n"
        f"📊 **Today:** {today_watched}/{limit}\n"
        f"👥 **Refers:** {total_refers}\n"
        f"🔗 **Link:** https://t.me/DesiMlh_bot?start=ref_{user_id}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📌 **Status:** Active\n"
        "🤖 **DESI MLH**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_text(profile_text, disable_web_page_preview=True)

# ৪. ভিডিও পাঠানোর কমান্ড (রেন্ডম ও ১০ মিনিট পর ওটো ডিলিট)
@app.on_message(filters.command("video") & filters.private)
async def send_random_video(client, message):
    user_id = message.from_user.id
    videos = await video_collection.find({"used_by": {"$ne": user_id}}).to_list(length=None)
    
    if not videos:
        return await message.reply_text("❌ আপনার দেখার মতো নতুন কোনো ভিডিও নেই!")

    target_video = random.choice(videos)
    sent_msg = await message.reply_video(
        video=target_video['file_id'],
        caption=f"{target_video['caption']}\n\n⚠️ এটি ১০ মিনিট পর ওটো ডিলিট হয়ে যাবে।"
    )
    
    await video_collection.update_one({"_id": target_video["_id"]}, {"$push": {"used_by": user_id}})
    await user_collection.update_one({"user_id": user_id}, {"$inc": {"watched_today": 1}})

    await asyncio.sleep(600)
    try:
        await sent_msg.delete()
    except:
        pass

# ৫. এডমিন মোড এবং ব্রডকাস্ট সিস্টেম
@app.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
async def admin_mode_on(client, message):
    if message.from_user.id not in ADMIN_MODE_USERS:
        ADMIN_MODE_USERS.append(message.from_user.id)
    
    admin_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🟢 **ADMIN MODE ACTIVATED**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "👑 Admin Mode: **ON**\n"
        "✅ You are now in Admin Mode\n"
        "📌 **নির্দেশনাঃ**\n"
        "🔹 সতর্কতার সাথে কমান্ড ব্যবহার করুন\n"
        "🔹 স্প্যাম বা অপ্রয়োজনীয় কাজ এড়িয়ে চলুন\n"
        "🔹 ইউজারদের সহায়তা করুন\n"
        "🔹 লগ ও রিপোর্ট চেক করুন\n"
        "🤖 **𝑫𝑬𝑺𝑰 𝑴𝑳𝑯**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_text(admin_text)

@app.on_message(filters.command("adminexit") & filters.user(ADMIN_IDS))
async def admin_mode_off(client, message):
    if message.from_user.id in ADMIN_MODE_USERS:
        ADMIN_MODE_USERS.remove(message.from_user.id)
    
    exit_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔴 **ADMIN MODE DEACTIVATED**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "👑 Admin Mode: **OFF**\n"
        "❌ You are no longer in Admin Mode\n"
        "📌 **Instructions:**\n"
        "🔹 You are in user mode now\n"
        "🔹 Admin commands will not work\n"
        "🔹 Login again to activate admin mode\n"
        "🤖 **DESI MLH**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_text(exit_text)

# ব্রডকাস্টিং (এডমিন মোড অন থাকলে যা লিখবেন তাই যাবে)
@app.on_message(filters.private & filters.user(ADMIN_IDS) & ~filters.command(["start", "admin", "adminexit", "video", "profile", "overview", "overview7days"]))
async def broadcast_handler(client, message):
    if message.from_user.id in ADMIN_MODE_USERS:
        all_users = await user_collection.find().to_list(length=None)
        count = 0
        for user in all_users:
            try:
                await message.copy(chat_id=user['user_id'])
                count += 1
                await asyncio.sleep(0.1)
            except:
                pass
        await message.reply_text(f"📢 ব্রডকাস্ট সম্পন্ন! {count} জন ইউজারের কাছে পাঠানো হয়েছে।")

# ৬. ওভারভিউ কমান্ডস
@app.on_message(filters.command("overview") & filters.user(ADMIN_IDS))
async def overview(client, message):
    total_users = await user_collection.count_documents({})
    blocked_users = await user_collection.count_documents({"is_blocked": True})
    active_users = total_users - blocked_users
    
    ov_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "📊 **COMMUNITY OVERVIEW**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: {total_users}\n"
        f"🟢 Active Users: {active_users}\n"
        f"🚫 Blocked Users: {blocked_users}\n"
        "📈 Community Status: Growing\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **DESI MLH Admin Panel**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_text(ov_text)

@app.on_message(filters.command("overview7days") & filters.user(ADMIN_IDS))
async def growth_report(client, message):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    target_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_data = {day: 0 for day in target_days}
    total_growth = 0
    for i in range(7):
        target_date = today - timedelta(days=i)
        day_name = target_date.strftime("%A")
        count = await user_collection.count_documents({"join_date": {"$gte": target_date, "$lt": target_date + timedelta(days=1)}})
        days_data[day_name] = count
        total_growth += count

    total_users = await user_collection.count_documents({})
    report_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "📈 **LAST 7 DAYS GROWTH REPORT**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📅 **Daily New Members:**\n"
        f"🗓 Monday: {days_data['Monday']}\n"
        f"🗓 Tuesday: {days_data['Tuesday']}\n"
        f"🗓 Wednesday: {days_data['Wednesday']}\n"
        f"🗓 Thursday: {days_data['Thursday']}\n"
        f"🗓 Friday: {days_data['Friday']}\n"
        f"🗓 Saturday: {days_data['Saturday']}\n"
        f"🗓 Sunday: {days_data['Sunday']}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Total Growth (7 Days): {total_growth}\n"
        f"👥 Total Users Overall: {total_users}\n"
        "📈 Community Trend: Growing\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **DESI MLH**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_text(report_text)

# ৭. গ্রুপ মডারেশন সিস্টেম
@app.on_message(filters.group & (filters.forwarded | filters.regex(r"(https?://[^\s]+)")))
async def mod_handler(client, message):
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ["administrator", "creator"]: return
    except: pass
    
    await message.delete()
    warn_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🚫 **OFFICIAL WARNING NOTICE**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Attention **{message.from_user.first_name}**\n"
        "❌ Forwarding messages is not allowed\n"
        "❌ Sharing external links is strictly prohibited\n"
        "📌 Please follow the group rules immediately.\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **DESI MLH Admin Panel**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    warn_msg = await message.reply_text(warn_text)
    await asyncio.sleep(30)
    try: await warn_msg.delete()
    except: pass

@app.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client, message):
    if not message.reply_to_message: return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]: return
    until = datetime.now() + timedelta(hours=2)
    await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, ChatPermissions(can_send_messages=False), until_date=until)
    await message.reply_text("✅ User muted for 2 hours.")

@app.on_message(filters.command("ban") & filters.group)
async def ban_cmd(client, message):
    if not message.reply_to_message: return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]: return
    await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.reply_text("✈️ User Banned Successfully.")

# ৮. ডাটাবেস চ্যানেল থেকে ভিডিও সেভ
@app.on_message(filters.chat(DATABASE_CHANNEL_ID) & (filters.video | filters.document))
async def save_video(client, message):
    file_id = message.video.file_id if message.video else message.document.file_id
    if not await video_collection.find_one({"file_id": file_id}):
        await video_collection.insert_one({"file_id": file_id, "caption": message.caption or "No Title", "used_by": []})

print("Bot Started Successfully...")
app.run()
