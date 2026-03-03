import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from main import ADMIN_IDS, user_collection

# সাময়িকভাবে ডাটা রাখার জন্য
pending_posts = {}

# ১. অ্যাডমিন প্যানেল কিবোর্ড
def get_admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Create Post", callback_data="create_post")],
        [InlineKeyboardButton("Scheduled Posts", callback_data="sched_posts"),
         InlineKeyboardButton("Edit Post", callback_data="edit_post")],
        [InlineKeyboardButton("Channel Stats", callback_data="chan_stats"),
         InlineKeyboardButton("Settings", callback_data="settings")]
    ])

# ২. পোস্ট ম্যানেজমেন্ট কিবোর্ড (নিচের বাটনগুলো)
def get_post_management_kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Delete All"), KeyboardButton("Preview")],
        [KeyboardButton("Cancel"), KeyboardButton("Send")]
    ], resize_keyboard=True)

@Client.on_callback_query(filters.user(ADMIN_IDS))
async def handle_admin_callbacks(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "create_post":
        pending_posts[user_id] = {"content": None, "buttons": []}
        await callback_query.message.edit_text(
            f"Here it is: \"{(await client.get_me()).first_name}\".\n\n"
            "Send me one or multiple messages you want to include in the post."
        )

    elif data == "add_button":
        guide_text = (
            "Send me a list of URL buttons for the message. Please use this format:\n\n"
            "`Button text 1 - http://www.example.com/`\n"
            "Use | to add up to three buttons in one row."
        )
        await callback_query.message.reply_text(guide_text, reply_markup=get_post_management_kb())

@Client.on_message(filters.private & filters.user(ADMIN_IDS))
async def process_broadcast_creation(client, message: Message):
    user_id = message.from_user.id
    if user_id not in pending_posts: return

    # বাটন ইনপুট প্রসেসিং
    if message.text and " - http" in message.text:
        rows = message.text.split("\n")
        for row in rows:
            line_btns = [InlineKeyboardButton(p.split(" - ")[0].strip(), url=p.split(" - ")[1].strip()) 
                         for p in row.split("|") if " - " in p]
            if line_btns: pending_posts[user_id]["buttons"].append(line_btns)
        await message.reply_text("✅ Buttons added!", reply_markup=get_post_management_kb())

    # কন্ট্রোল বাটন লজিক (Send/Cancel)
    elif message.text == "Send":
        post = pending_posts[user_id]
        if not post["content"]: return await message.reply_text("❌ কোনো কন্টেন্ট নেই!")
        
        del pending_posts[user_id]
        await message.reply_text("━━━━━━━━━━━━━━━━━━━\n📢 **BROADCAST STARTED**\n━━━━━━━━━━━━━━━━━━━\n🚀 A new broadcast has been initiated.\n📤 Messages are being sent to all users.\n⏳ Please wait until the process is completed.\n⚙️ Do not interrupt the system during this time.\n━━━━━━━━━━━━━━━━━━━\n🤖 **DESI MLH ADMIN BROADCAST**\n━━━━━━━━━━━━━━━━━━━", reply_markup=ReplyKeyboardRemove())
        
        users = await user_collection.find().to_list(length=None)
        for u in users:
            try:
                await post["content"].copy(chat_id=u["user_id"], reply_markup=InlineKeyboardMarkup(post["buttons"]))
                await asyncio.sleep(0.05)
            except: pass
            
        await message.reply_text("━━━━━━━━━━━━━━━━━━━\n✅ **BROADCAST COMPLETED**\n━━━━━━━━━━━━━━━━━━━\n📬 Broadcast has been successfully delivered.\n📊 All users have received the message.\n🎉 Process finished without interruption.\n━━━━━━━━━━━━━━━━━━━\n🤖 **DESI MLH ADMIN BROADCAST**\n━━━━━━━━━━━━━━━━━━━")

    elif message.text == "Cancel":
        del pending_posts[user_id]
        await message.reply_text("❌ Post creation cancelled.", reply_markup=ReplyKeyboardRemove())
        await admin_panel_show(client, message)

    else:
        pending_posts[user_id]["content"] = message
        preview_markup = InlineKeyboardMarkup(pending_posts[user_id]["buttons"] + [[InlineKeyboardButton("Add Button", callback_data="add_button")]])
        await message.reply_text("✨ **Post Preview:**", reply_markup=preview_markup)

async def admin_panel_show(client, message):
    await message.reply_text("Welcome to Admin Control Panel", reply_markup=get_admin_keyboard())
    # এটি সকল সাধারণ মেসেজের জন্য গ্লোবাল হ্যান্ডলার হিসেবে কাজ করবে
@Client.on_message(filters.private & ~filters.user(ADMIN_IDS) & ~filters.command(["start", "admin"]))
async def global_button_reply(client, message):
    # যে বাটনগুলো তুই সব মেসেজের নিচে দেখাতে চাস
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url="https://t.me/YourBotUsername?startgroup=true")],
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/DesiMlh"),
         InlineKeyboardButton("🔞 VIP Content", url="https://t.me/+1apgXrLWXuE4M2Y1")]
    ])
    
    # ইউজার মেসেজ দিলে বট তার উত্তর হিসেবে এই বাটনগুলো দেবে
    try:
        await message.reply_text(
            "Thanks for your message! \nJoin our community for the latest updates:",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error in global button: {e}")
@Client.on_message(filters.private & ~filters.user(ADMIN_IDS) & ~filters.command(["start", "admin"]))
async def auto_button(client, message):
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Channel", url="https://t.me/DesiMlh")]])
    await message.reply_text("Check our channel:", reply_markup=markup)
