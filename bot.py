"""
╔══════════════════════════════════════════════════════════════╗
║          TELEGRAM VIDEO & REFERRAL BOT                       ║
║          Pyrogram  •  Motor (MongoDB)  •  Python 3.11+       ║
╚══════════════════════════════════════════════════════════════╝

Entry point — initialises the Pyrogram client, connects to MongoDB,
starts background tasks, and runs the bot via plugin auto-discovery.
"""

import asyncio
import logging
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, validate_config
from database import init_db
from utils.reset_daily import reset_daily_limits_loop

logger = logging.getLogger("BOT")


def create_app() -> Client:
    """Build and return the Pyrogram Client."""
    return Client(
        name="video_referral_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="handlers"),
        parse_mode=ParseMode.HTML,   # ← default parse_mode for all messages
        workers=8,
    )


async def main():
    # ── Validate environment ────────────────────────────────────
    validate_config()

    # ── Create client ───────────────────────────────────────────
    app = create_app()

    async with app:
        # ── Database indexes ────────────────────────────────────
        await init_db()

        me = await app.get_me()
        logger.info(f"Bot started  →  @{me.username}  (ID: {me.id})")

        # ── Background: daily-limit reset ───────────────────────
        asyncio.create_task(reset_daily_limits_loop())

        # ── Keep alive ──────────────────────────────────────────
        logger.info("Listening for updates…")
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
