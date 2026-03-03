from pyrogram import Client, filters
from datetime import datetime

# তোর লগ পাঠানোর গ্রুপের আইডি এখানে দে (অবশ্যই মাইনাস সহ)
LOG_GROUP_ID = -1003744642897 

@Client.on_chat_join_request()
async def join_log_handler(client, message):
    chat = message.chat           # যে গ্রুপে রিকোয়েস্ট এসেছে
    user = message.from_user       # যে ইউজার রিকোয়েস্ট দিয়েছে
    
    # লগ মেসেজের ফরম্যাট
    log_text = (
        "📢 **Auto Approval Log**\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **User:** {user.first_name}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"👥 **Group:** {chat.title}\n"
        f"📅 **Time:** {datetime.now().strftime('%I:%M %p | %d %b')}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "✅ **Status:** User Approved & Messaged"
    )

    try:
        # তোর গ্রুপে তথ্যটি পাঠিয়ে দেবে
        await client.send_message(chat_id=LOG_GROUP_ID, text=log_text)
    except Exception as e:
        print(f"Log Error: {e}")
