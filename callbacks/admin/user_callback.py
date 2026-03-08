from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database.users import get_user
from database.referrals import get_user_referrals

@Client.on_callback_query(filters.regex("my_status"))
async def my_status(client, query: CallbackQuery):

    user_id = query.from_user.id

    user = await get_user(user_id)
    referrals = await get_user_referrals(user_id)

    text = f"""
👤 **Your Status**

🆔 User ID: `{user_id}`
👥 Total Referrals: {referrals}
💎 Premium: {user['premium']}

Keep inviting friends to rank on leaderboard!
"""

    await query.message.edit_text(text)