"""
User-facing handlers:
  /start          — register + welcome
  /video          — random video with daily limit
  /me  | /status  — profile card
  Callback queries — inline button actions
  Auto join-request approval
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from database import (
    add_user,
    get_user,
    check_and_reset_daily,
    increment_video_used,
    get_random_video,
)
from config import (
    LOG_GROUP_ID,
    VIDEO_AUTO_DELETE_SECONDS,
    VIP_LINK,
    ADMIN_USERNAME,
    REFERRAL_BONUS,
)
from utils.referral import process_referral

logger = logging.getLogger("USER")


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

async def _bot_username(client: Client) -> str:
    return (await client.get_me()).username


async def _ref_link(client: Client, user_id: int) -> str:
    return f"https://t.me/{await _bot_username(client)}?start={user_id}"


# ═══════════════════════════════════════════════════════════════
#  /start
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or ""

    # ── Parse referral param ────────────────────────────────────
    referred_by = None
    if len(message.command) > 1:
        try:
            ref_id = int(message.command[1])
            if ref_id != user_id:          # block self-referral early
                referred_by = ref_id
        except ValueError:
            pass

    # ── Save user ───────────────────────────────────────────────
    is_new = await add_user(user_id, first_name, username, referred_by)

    # ── Process referral (only for genuinely new users) ─────────
    if is_new and referred_by:
        await process_referral(client, user_id, referred_by)

    # ── Welcome message ─────────────────────────────────────────
    ref_link = await _ref_link(client, user_id)
    welcome = (
        f"<b>👋 Welcome, {first_name}!</b>\n\n"
        f"I'm your <b>Video & Referral Bot</b>.\n\n"
        f"📹  /video  — Get a random video\n"
        f"👤  /me     — View your profile\n"
        f"🔗  Share your referral link to unlock more daily videos!\n\n"
        f"<b>Your Referral Link:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"💎 <b>Want unlimited access?</b>\n"
        f"👉 <a href='{VIP_LINK}'>Join VIP Channel</a>\n"
        f"📩 Contact: @{ADMIN_USERNAME}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📹 Get Video", callback_data="get_video"),
                InlineKeyboardButton("👤 My Profile", callback_data="my_profile"),
            ],
            [
                InlineKeyboardButton("🔗 Referral Link", callback_data="referral_link"),
                InlineKeyboardButton("💎 VIP Access", url=VIP_LINK),
            ],
            [
                InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}"),
            ],
        ]
    )

    await message.reply(welcome, reply_markup=keyboard, disable_web_page_preview=True)

    # ── Log to group ────────────────────────────────────────────
    if is_new and LOG_GROUP_ID:
        try:
            await client.send_message(
                LOG_GROUP_ID,
                f"<b>🆕 New User</b>\n\n"
                f"<b>Name:</b>  {first_name}\n"
                f"<b>Username:</b>  @{username or 'N/A'}\n"
                f"<b>ID:</b>  <code>{user_id}</code>\n"
                f"<b>Referred by:</b>  <code>{referred_by or 'Direct'}</code>",
            )
        except Exception as e:
            logger.error(f"Log-group send failed: {e}")


# ═══════════════════════════════════════════════════════════════
#  /me  |  /status   — Profile Card
# ═══════════════════════════════════════════════════════════════

async def _send_profile(client: Client, user_id: int, chat_id: int):
    await check_and_reset_daily(user_id)
    user = await get_user(user_id)
    if not user:
        await client.send_message(chat_id, "<b>❌ Not registered. Send /start first.</b>")
        return

    remaining = max(0, user["daily_video_limit"] - user["today_video_used"])
    ref_link = await _ref_link(client, user_id)

    text = (
        f"<b>👤 Your Profile</b>\n"
        f"{'━' * 28}\n\n"
        f"<b>🆔 User ID:</b>       <code>{user['user_id']}</code>\n"
        f"<b>📛 Name:</b>          {user['first_name']}\n"
        f"<b>📅 Joined:</b>        {user['join_date'].strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"<b>📹 Daily Limit:</b>   {user['daily_video_limit']}\n"
        f"<b>📊 Used Today:</b>    {user['today_video_used']}\n"
        f"<b>📈 Remaining:</b>     {remaining}\n\n"
        f"<b>👥 Referrals:</b>     {user['referral_count']}\n\n"
        f"<b>🔗 Referral Link:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"{'━' * 28}\n"
        f"💎 <a href='{VIP_LINK}'>Join VIP</a>  •  📩 @{ADMIN_USERNAME}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📹 Get Video", callback_data="get_video"),
                InlineKeyboardButton("🔗 Refer Friends", callback_data="referral_link"),
            ],
            [
                InlineKeyboardButton("💎 VIP Access", url=VIP_LINK),
            ],
        ]
    )

    await client.send_message(
        chat_id, text, reply_markup=keyboard, disable_web_page_preview=True
    )


@Client.on_message(filters.command(["me", "status"]) & filters.private)
async def profile_handler(client: Client, message: Message):
    await _send_profile(client, message.from_user.id, message.chat.id)


# ═══════════════════════════════════════════════════════════════
#  /video  — Random Video
# ═══════════════════════════════════════════════════════════════

async def _send_video(client: Client, user_id: int, chat_id: int):
    await check_and_reset_daily(user_id)
    user = await get_user(user_id)

    if not user:
        await client.send_message(chat_id, "<b>❌ Not registered. Send /start first.</b>")
        return

    # ── Limit check ─────────────────────────────────────────────
    if user["today_video_used"] >= user["daily_video_limit"]:
        ref_link = await _ref_link(client, user_id)

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔗 Share Referral", callback_data="referral_link"),
                    InlineKeyboardButton("💎 Get VIP", url=VIP_LINK),
                ],
                [
                    InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}"),
                ],
            ]
        )

        await client.send_message(
            chat_id,
            f"<b>⚠️ Daily Limit Reached!</b>\n\n"
            f"You've used all <b>{user['daily_video_limit']}</b> videos for today.\n\n"
            f"💡 <b>Tip 1:</b> Refer friends to get <b>+{REFERRAL_BONUS}</b> extra daily videos!\n"
            f"💎 <b>Tip 2:</b> <a href='{VIP_LINK}'>Join VIP</a> for unlimited access!\n\n"
            f"<b>🔗 Your Referral Link:</b>\n<code>{ref_link}</code>\n\n"
            f"📩 Need help? Contact @{ADMIN_USERNAME}",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        return

    # ── Fetch random video ──────────────────────────────────────
    video = await get_random_video()
    if not video:
        await client.send_message(
            chat_id,
            f"<b>❌ No videos in the database yet.</b>\n\n"
            f"📩 Contact @{ADMIN_USERNAME} to report this issue.",
        )
        return

    # ── Send video ──────────────────────────────────────────────
    try:
        usage = user["today_video_used"] + 1
        limit = user["daily_video_limit"]

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📹 Next Video", callback_data="get_video"),
                    InlineKeyboardButton("💎 VIP Access", url=VIP_LINK),
                ],
            ]
        )

        sent = await client.send_video(
            chat_id=chat_id,
            video=video["file_id"],
            caption=(
                f"<b>📹 Random Video</b>\n\n"
                f"<b>📊 Usage:</b> {usage}/{limit}\n"
                f"<i>⏱ Auto-deletes in {VIDEO_AUTO_DELETE_SECONDS // 60} minutes</i>\n\n"
                f"💎 <a href='{VIP_LINK}'>Join VIP</a>  •  📩 @{ADMIN_USERNAME}"
            ),
            reply_markup=keyboard,
        )

        await increment_video_used(user_id)

        # Log
        if LOG_GROUP_ID:
            try:
                await client.send_message(
                    LOG_GROUP_ID,
                    f"<b>📹 Video Sent</b>\n"
                    f"User: {user['first_name']} (<code>{user_id}</code>)\n"
                    f"Usage: {usage}/{limit}",
                )
            except Exception:
                pass

        # Auto-delete after N seconds
        await asyncio.sleep(VIDEO_AUTO_DELETE_SECONDS)
        try:
            await sent.delete()
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Video send error for {user_id}: {e}")
        await client.send_message(
            chat_id,
            f"<b>❌ Failed to send video. Please try again.</b>\n\n"
            f"📩 If this persists, contact @{ADMIN_USERNAME}",
        )


@Client.on_message(filters.command("video") & filters.private)
async def video_handler(client: Client, message: Message):
    await _send_video(client, message.from_user.id, message.chat.id)


# ═══════════════════════════════════════════════════════════════
#  CALLBACK QUERIES
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("^get_video$"))
async def cb_video(client: Client, cq: CallbackQuery):
    await cq.answer("⏳ Fetching video…")
    await _send_video(client, cq.from_user.id, cq.message.chat.id)


@Client.on_callback_query(filters.regex("^my_profile$"))
async def cb_profile(client: Client, cq: CallbackQuery):
    await cq.answer()
    await _send_profile(client, cq.from_user.id, cq.message.chat.id)


@Client.on_callback_query(filters.regex("^referral_link$"))
async def cb_referral(client: Client, cq: CallbackQuery):
    ref_link = await _ref_link(client, cq.from_user.id)
    await cq.answer()

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💎 VIP Access", url=VIP_LINK)],
        ]
    )

    await cq.message.reply(
        f"<b>🔗 Your Referral Link</b>\n\n"
        f"<code>{ref_link}</code>\n\n"
        f"<i>Share this link — you earn <b>+{REFERRAL_BONUS}</b> daily videos per new referral!</i>\n\n"
        f"💎 Or <a href='{VIP_LINK}'>join VIP</a> for unlimited access!",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# ═══════════════════════════════════════════════════════════════
#  AUTO-APPROVE JOIN REQUESTS
# ═══════════════════════════════════════════════════════════════

@Client.on_chat_join_request()
async def auto_approve(client: Client, join_request: ChatJoinRequest):
    try:
        await join_request.approve()
        user = join_request.from_user
        await add_user(user.id, user.first_name or "User", user.username or "")

        bot_un = await _bot_username(client)

        try:
            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🚀 Start Bot", url=f"https://t.me/{bot_un}?start=approved")],
                ]
            )

            await client.send_message(
                user.id,
                f"<b>✅ Your join request has been approved!</b>\n\n"
                f"Send /start to begin using the bot.\n\n"
                f"📩 Contact: @{ADMIN_USERNAME}",
                reply_markup=keyboard,
            )
        except Exception:
            pass

        if LOG_GROUP_ID:
            try:
                await client.send_message(
                    LOG_GROUP_ID,
                    f"<b>✅ Join Request Approved</b>\n"
                    f"User: {user.first_name} (<code>{user.id}</code>)",
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Auto-approve error: {e}")
