import urllib.parse
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime

# ১. জয়েন রিকোয়েস্ট হ্যান্ডলার ও কাস্টম মেসেজ
@Client.on_chat_join_request()
async def auto_approve_and_message(client, request: ChatJoinRequest):
    chat = request.chat
    user = request.from_user
    
    # জয়েন রিকোয়েস্ট এপ্রুভ করা
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    
    # ইনবক্সে পাঠানোর মেসেজ ফরম্যাট
    welcome_text = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "✅ **JOIN REQUEST APPROVED**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** {user.first_name}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"🔗 **Username:** @{user.username if user.username else 'None'}\n\n"
        f"🎉 Your request has been approved!\n"
        f"Welcome to **{chat.title}** 🎊\n\n"
        "🎬 To watch videos, use the command below:\n"
        "👉 /video\n\n"
        "📌 Please follow the group rules and stay active.\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **DESI MLH SYSTEM**\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    # প্রিমিয়াম মেসেজ ইউআরএল এনকোডিং
    premium_msg = (
        "Hello Admin 👋\n"
        "I would like to upgrade to Premium Membership in this community.\n"
        "🚀 I’m interested in accessing exclusive features and premium content.\n"
        "Please let me know the process, requirements, and payment details.\n"
        "Looking forward to your response.\n"
        "Thank you 💖"
    )
    encoded_premium_msg = urllib.parse.quote(premium_msg)

    # বাটন সেটআপ (তোর দেওয়া ফরম্যাট অনুযায়ী)
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD ME TO GROUP", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true"),
         InlineKeyboardButton("🔞 VIP🫦", url="https://t.me/+1apgXrLWXuE4M2Y1")],
        [InlineKeyboardButton("👤 MY STATUS", callback_data="my_status"), 
         InlineKeyboardButton("💎 BUY PREMIUM", url=f"https://t.me/IH_Maruf?text={encoded_premium_msg}")],
        [InlineKeyboardButton("📊 Referral Info", callback_data="ref_info")]
    ])

    try:
        await client.send_message(
            chat_id=user.id,
            text=welcome_text,
            reply_markup=buttons
        )
    except Exception as e:
        print(f"Error sending message: {e}")

# ২. বাটন ক্লিক হ্যান্ডলার (Status এবং Referral)
# অ্যাডমিন আইডি সরাসরি দেওয়া হলো যাতে লগে এরর না আসে
MY_ADMIN_IDS = [6770328841]

@Client.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    bot = await client.get_me()
    
    # বাটন সেটআপ (সব মেসেজের নিচে রাখার জন্য)
    premium_msg = "Hello Admin 👋\nI would like to upgrade to Premium Membership..."
    encoded_premium_msg = urllib.parse.quote(premium_msg)
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD ME TO GROUP", url=f"https://t.me/{bot.username}?startgroup=true"),
         InlineKeyboardButton("🔞 VIP** 🫦", url="https://t.me/+1apgXrLWXuE4M2Y1")],
        [InlineKeyboardButton("👤 MY STATUS", callback_data="my_status"), 
         InlineKeyboardButton("💎 BUY PREMIUM", url=f"https://t.me/IH_Maruf?text={encoded_premium_msg}")],
        [InlineKeyboardButton("📊 Referral Info", callback_data="ref_info")]
    ])

    # ডাটাবেস থেকে তথ্য আনা
    try:
        from main import user_collection 
        user_data = await user_collection.find_one({"user_id": user_id})
    except:
        user_data = None

    # ১. MY STATUS ক্লিক করলে মেসেজ আসবে
    if callback_query.data == "my_status":
        status_text = (
            "👤 **YOUR PROFILE STATUS**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"📅 **Joined:** {user_data['join_date'].strftime('%Y-%m-%d') if user_data and 'join_date' in user_data else 'N/A'}\n"
            f"🎥 **Watched Today:** {user_data['watched_today'] if user_data and 'watched_today' in user_data else 0}\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        status_msg = await callback_query.message.reply_text(status_text, reply_markup=reply_markup)
await callback_query.answer()
await asyncio.sleep(30) # ৩০ সেকেন্ড ওয়েট
try:
    await status_msg.delete() # মেসেজ ডিলিট
except:
    pass

    # ২. Referral Info ক্লিক করলে তোর দেওয়া ফরমেটে মেসেজ আসবে
    elif callback_query.data == "ref_info":
        total_refers = user_data.get('refers', 0) if user_data else 0
        successful_refers = total_refers 
        pending_refers = 0
        reward_status = "Claimable" if total_refers > 5 else "In Progress"

        ref_report = (
            "━━━━━━━━━━━━━━━━━━━\n"
            "🎯 **REFERRAL STATUS REPORT**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User:** {first_name}\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"👥 **Total Referrals:** {total_refers}\n"
            f"✅ **Successful Referrals:** {successful_refers}\n"
            f"⏳ **Pending Referrals:** {pending_refers}\n\n"
            "🔗 **Your Referral Link:**\n"
            f"https://t.me/{bot.username}?start=ref_{user_id}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 **Reward Status:** {reward_status}\n"
            "📈 Keep sharing to earn more rewards!\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🤖 **DESI MLH REFERRAL**\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        await callback_query.message.reply_text(ref_report, reply_markup=reply_markup)
        await callback_query.answer()
