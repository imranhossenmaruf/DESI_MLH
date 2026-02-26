"""
Group security handlers:
  - Delete messages containing links (http / https / t.me)
  - Delete forwarded messages
  - Send auto-deleting warning
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from config import WARNING_AUTO_DELETE_SECONDS, ADMIN_USERNAME

logger = logging.getLogger("SECURITY")

# ─── Blocked keywords ───────────────────────────────────────────
LINK_KEYWORDS = ("http://", "https://", "t.me/", "t.me/+")


async def _is_group_admin(client: Client, chat_id: int, user_id: int) -> bool:
    """Return True if the user is an admin/owner of the chat."""
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )
    except Exception:
        return False


async def _warn_and_cleanup(client: Client, chat_id: int, name: str, reason: str):
    """Send a warning that auto-deletes after N seconds."""
    warning = await client.send_message(
        chat_id,
        f"<b>⚠️ Warning</b>\n\n"
        f"<b>{name}</b>, {reason}\n\n"
        f"📩 Contact @{ADMIN_USERNAME} if you think this is a mistake.\n"
        f"<i>This warning will disappear in {WARNING_AUTO_DELETE_SECONDS}s.</i>",
    )
    await asyncio.sleep(WARNING_AUTO_DELETE_SECONDS)
    try:
        await warning.delete()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
#  LINK FILTER  (text / caption messages, excluding forwarded)
# ═══════════════════════════════════════════════════════════════

@Client.on_message(
    filters.group & (filters.text | filters.caption) & ~filters.forwarded
)
async def link_filter(client: Client, message: Message):
    if not message.from_user:
        return

    # Don't filter group admins
    if await _is_group_admin(client, message.chat.id, message.from_user.id):
        return

    text = (message.text or message.caption or "").lower()

    if not any(kw in text for kw in LINK_KEYWORDS):
        return

    try:
        await message.delete()
        logger.info(
            f"Link deleted from {message.from_user.id} in {message.chat.id}"
        )
        await _warn_and_cleanup(
            client,
            message.chat.id,
            message.from_user.first_name,
            "links are <b>not allowed</b> in this group.",
        )
    except Exception as e:
        logger.error(f"Link filter error: {e}")


# ═══════════════════════════════════════════════════════════════
#  FORWARDED MESSAGE FILTER
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.group & filters.forwarded)
async def forward_filter(client: Client, message: Message):
    if not message.from_user:
        return

    if await _is_group_admin(client, message.chat.id, message.from_user.id):
        return

    try:
        await message.delete()
        logger.info(
            f"Forward deleted from {message.from_user.id} in {message.chat.id}"
        )
        await _warn_and_cleanup(
            client,
            message.chat.id,
            message.from_user.first_name,
            "forwarded messages are <b>not allowed</b> in this group.",
        )
    except Exception as e:
        logger.error(f"Forward filter error: {e}")
