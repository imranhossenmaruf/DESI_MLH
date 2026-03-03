import asyncio
import random
import re
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse  # এটিও যোগ কর, বাটন লিংকের টেক্সট এনকোড করার জন্য
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
BROADCAST_DATA = {}

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
# গ্রুপ ডাটা সেভ করার লজিক
@app.on_message(filters.group & ~filters.service)
async def save_group(client, message):
    chat_id = message.chat.id
    if not await user_collection.find_one({"user_id": chat_id}):
        await user_collection.insert_one({
            "user_id": chat_id,
            "type": "group",
            "join_date": datetime.now()
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
# ৫. এডমিন মোড অন/অফ কমান্ড (তোর কাস্টম ফরম্যাট)
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def admin_mode_on(client, message):
    if message.from_user.id not in ADMIN_MODE_USERS:
        ADMIN_MODE_USERS.append(message.from_user.id)
    await message.reply_text (
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

@app.on_message(filters.command("broadcastoff") & filters.user(ADMIN_IDS))
async def admin_mode_off(client, message):
    if message.from_user.id in ADMIN_MODE_USERS:
        ADMIN_MODE_USERS.remove(message.from_user.id)
    await message.reply_text (
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

# ৬. ব্রডকাস্ট উইজার্ড
# ৬. ব্রডকাস্ট উইজার্ড (মেসেজ রিসিভ করা - এটি তোর ফাইলে মিসিং ছিল)
@app.on_message(filters.private & filters.user(ADMIN_IDS) & ~filters.command(["start", "admin", "adminexit", "video", "profile", "overview", "overview7days"]) & ~filters.regex(r"\|"))
async def broadcast_wizard(client, message):
    if message.from_user.id in ADMIN_MODE_USERS:
        user_id = message.from_user.id
        # মূল মেসেজটি সেভ রাখা হচ্ছে
        BROADCAST_DATA[user_id] = {"message": message, "btn_name": None, "btn_url": None}

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 SET BUTTON URL", callback_data="set_btn_url")],
            [InlineKeyboardButton("🚀 SEND NOW (No Button)", callback_data="confirm_bc")]
        ])
        await message.reply_text("📝 মেসেজ পাওয়া গেছে! বাটন এড করতে চাস?", reply_markup=buttons)

# বাটন সেট ও ব্রডকাস্ট কনফার্ম করার কলব্যাক
@app.on_callback_query(filters.regex(r"^(set_btn_url|confirm_bc)$"))
async def handle_bc_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if callback_query.data == "set_btn_url":
        await callback_query.message.edit_text("⌨️ বাটন সেট করতে নিচের ফরম্যাটে রিপ্লাই দাও:\n\n`নাম | লিঙ্ক` \n\nযেমন: `Join | https://t.me/example` ")
    elif callback_query.data == "confirm_bc":
        await send_the_broadcast(client, callback_query.message, user_id)

# বাটন ডিটেইলস রিসিভ করা (মূল মেসেজ পরিবর্তন না করে শুধু বাটন আপডেট হবে)
@app.on_message(filters.private & filters.user(ADMIN_IDS) & filters.regex(r"\|"))
async def receive_btn_details(client, message):
    user_id = message.from_user.id
    if user_id in BROADCAST_DATA:
        try:
            parts = message.text.split("|")
            BROADCAST_DATA[user_id]["btn_name"] = parts[0].strip()
            BROADCAST_DATA[user_id]["btn_url"] = parts[1].strip()
            
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 START BROADCAST", callback_data="confirm_bc")]])
            await message.reply_text(
                f"✅ **বাটন সেভ হয়েছে!**\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🏷️ নাম: {parts[0].strip()}\n"
                f"🔗 লিঙ্ক: {parts[1].strip()}\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"এখন ব্রডকাস্ট শুরু করতে নিচের বাটনে ক্লিক কর।", 
                reply_markup=buttons
            )
        except Exception as e:
            await message.reply_text(f"❌ ফরম্যাট ভুল! 'নাম | লিঙ্ক' এভাবে দাও।")
# ব্রডকাস্ট পাঠানোর মূল ইঞ্জিন (ইউজার + গ্রুপ সবার জন্য)
async def send_the_broadcast(client, status_msg, admin_id):
    data = BROADCAST_DATA.get(admin_id)
    if not data: 
        return await status_msg.edit_text("❌ ডাটা পাওয়া যায়নি!")
        
    # ডাটাবেস থেকে ইউজার এবং গ্রুপ সবার আইডি তুলে আনা হচ্ছে
    all_targets = await user_collection.find().to_list(length=None)
    
    btn = None
    if data["btn_name"] and data["btn_url"]:
        btn = InlineKeyboardMarkup([[InlineKeyboardButton(data["btn_name"], url=data["btn_url"])]])

    await status_msg.edit_text(f"⏳ ব্রডকাস্টিং শুরু হয়েছে...\nমোট লক্ষ্য (ইউজার+গ্রুপ): {len(all_targets)}")
    
    count = 0
    for target in all_targets:
        try:
            # copy() ব্যবহার করে মেসেজ পাঠানো হচ্ছে
            sent = await data["message"].copy(chat_id=target['user_id'], reply_markup=btn)
            
            # যদি এটি গ্রুপ হয় (ID < 0), তবে মেসেজটি পিন করে দেবে
            if target['user_id'] < 0:
                try:
                    await sent.pin(disable_notification=False)
                except:
                    pass
                    
            count += 1
            await asyncio.sleep(0.05) # Flood wait এড়াতে সামান্য বিরতি
        except:
            pass
            
    await status_msg.edit_text(f"✅ **ব্রডকাস্ট সম্পন্ন!**\n━━━━━━━━━━━━━━━━━━━\n📤 মোট পাঠানো হয়েছে: `{count}`\n━━━━━━━━━━━━━━━━━━━")
    if admin_id in BROADCAST_DATA: 
        del BROADCAST_DATA[admin_id]
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

    # ১. বাটন সেটআপ (তোর আগের কোডের ফরম্যাট অনুযায়ী)
    bot = await client.get_me()
    premium_msg = (
        "Hello Admin 👋\n"
    "I would like to upgrade to Premium Membership in this community.\n"
    "🚀 I’m interested in accessing exclusive features and premium content.\n"
    "Please let me know the process, requirements, and payment details.\n"
    "Looking forward to your response.\n"
    "Thank you 💖"
    )
    encoded_premium_msg = urllib.parse.quote(premium_msg)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD ME TO GROUP", url=f"https://t.me/{bot.username}?startgroup=true"),
         InlineKeyboardButton("🔞 VIP🫦", url="https://t.me/+1apgXrLWXuE4M2Y1")],
        [InlineKeyboardButton("👤 MY STATUS", callback_data="my_status"), 
         InlineKeyboardButton("💎 BUY PREMIUM", url=f"https://t.me/IH_Maruf?text={encoded_premium_msg}")],
        [InlineKeyboardButton("📊 Referral Info", callback_data="ref_info")]
    ])

    # ২. ওয়ার্নিং টেক্সট
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

    # ৩. বাটনসহ মেসেজ পাঠানো
    warn_msg = await message.reply_text(warn_text, reply_markup=buttons)

    # ৩০ সেকেন্ড পর ওয়ার্নিং মেসেজ ডিলিট করা
    await asyncio.sleep(30)
    try: 
        await warn_msg.delete()
    except: 
        pass

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
# --- জয়েন রিকোয়েস্ট হ্যান্ডলার (মেসেজ ও বাটনসহ) ---
@app.on_chat_join_request()
async def auto_approve_and_save_user(client, message):
    user = message.from_user
    chat = message.chat
    bot = await client.get_me()
    
    # ১. ডেটাবেসে ইউজার সেভ করা (ইউজার সংখ্যা বাড়াতে)
    if not await user_collection.find_one({"user_id": user.id}):
        await user_collection.insert_one({
            "user_id": user.id,
            "type": "private",
            "is_blocked": False,
            "join_date": datetime.now(),
            "refers": 0,
            "watched_today": 0
        })

    # ২. রিকোয়েস্ট এপ্রুভ ও কাস্টম মেসেজ পাঠানো
    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        
        user_name = f"@{user.username}" if user.username else "No Username"
        
        # প্রিমিয়াম মেসেজ এনকোডিং
        premium_msg = ("Hello Admin 👋\nI would like to upgrade to Premium Membership.")
        encoded_premium_msg = urllib.parse.quote(premium_msg)

        # তোর দেওয়া বাটন সেটআপ
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ADD ME TO GROUP", url=f"https://t.me/{bot.username}?startgroup=true"),
             InlineKeyboardButton("🔞 VIP🫦", url="https://t.me/+1apgXrLWXuE4M2Y1")],
            [InlineKeyboardButton("👤 MY STATUS", callback_data="my_status"), 
             InlineKeyboardButton("💎 BUY PREMIUM", url=f"https://t.me/IH_Maruf?text={encoded_premium_msg}")],
            [InlineKeyboardButton("📊 Referral Info", callback_data="ref_info")]
        ])

        welcome_text = (
            "━━━━━━━━━━━━━━━━━━━\n"
            "✅ **JOIN REQUEST APPROVED**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** {user.first_name}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"🔗 **Username:** {user_name}\n\n"
            "🎉 Your request has been approved!\n"
            f"Welcome to **{chat.title}** 🎊\n\n"
            "🎬 To watch videos, use the command below:\n"
            "👉 /video\n\n"
            "📌 Please follow the group rules and stay active.\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🤖 **DESI MLH SYSTEM**\n"
            "━━━━━━━━━━━━━━━━━━━"
        )

        # ইউজারকে মেসেজ পাঠানোর চেষ্টা
        try:
            await client.send_message(chat_id=user.id, text=welcome_text, reply_markup=buttons)
        except:
            pass 

    except Exception as e:
        print(f"Error Approving: {e}")

    # ৩. তোর লগ গ্রুপে তথ্য পাঠানো
    LOG_GROUP_ID = -1003744642897 
    try:
        await client.send_message(chat_id=LOG_GROUP_ID, text=f"🔔 **Approved & Saved:** {user.first_name}")
    except:
    # ৩. লগ পাঠানো শেষ
    pass

if __name__ == "__main__":
    print("Bot Started Successfully...")
    app.run()

