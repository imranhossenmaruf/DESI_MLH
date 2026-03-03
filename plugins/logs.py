from pyrogram import Client, filters
from datetime import datetime

# এখানে তোর সঠিক আইডিটি বসিয়ে দে
LOG_GROUP_ID = -1003744642897

@Client.on_chat_join_request()
async def join_log_handler(client, message):
    try:
        chat = message.chat
        user = message.from_user
        
        log_text = (
            "📢 **Auto Approval Log**\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User:** {user.first_name}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"👥 **Group:** {chat.title}\n"
            f"📅 **Time:** {datetime.now().strftime('%I:%M %p')}\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        
        # মেসেজ পাঠানোর চেষ্টা
        await client.send_message(chat_id=LOG_GROUP_ID, text=log_text)
        print(f"Log sent for {user.first_name}")
    except Exception as e:
        print(f"Log Error: {e}") # এটি চেক করবি তোর টার্মিনালে কোনো এরর আসে কিনা
