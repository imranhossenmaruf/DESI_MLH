from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME

start_buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "➕ Add Me To Group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                "💎 VIP",
                url="https://t.me/YOUR_CHANNEL_LINK"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 MY STATUS",
                callback_data="my_status"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 BUY PREMIUM",
                url="https://t.me/IH_Maruf?text=I%20want%20to%20buy%20premium%20access%20of%20your%20bot"
            )
        ],
        [
            InlineKeyboardButton(
                "🏆 LEADERBOARD",
                callback_data="leaderboard"
            )
        ]
    ]
)