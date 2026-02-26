"""
Background task that periodically resets daily video usage counters
for all users in bulk.  Runs every hour via asyncio.
"""

import asyncio
import logging
from database import bulk_reset_daily

logger = logging.getLogger("DAILY_RESET")


async def reset_daily_limits_loop():
    """
    Infinite loop — checks every hour.
    Resets `today_video_used` and updates `last_reset_date` for any
    user whose stored date doesn't match today (UTC).
    """
    logger.info("Daily-reset background task started")

    while True:
        try:
            modified = await bulk_reset_daily()
            if modified:
                logger.info(f"Reset daily limits for {modified} user(s)")
        except Exception as e:
            logger.error(f"Daily-reset error: {e}", exc_info=True)

        await asyncio.sleep(3600)  # run every 1 hour
