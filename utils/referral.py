"""
Referral processing logic.
Handles validation, duplicate prevention, and referrer notification.
"""

import logging
from database import get_user, increment_referral
from config import REFERRAL_BONUS

logger = logging.getLogger("REFERRAL")


async def process_referral(client, new_user_id: int, referrer_id: int) -> bool:
    """
    Process a referral link.

    Returns True if the referral was valid and credited.
    Guards:
      - No self-referral
      - Referrer must exist in DB
      - New user must actually be new (handled upstream in add_user)
    """

    # ── Guard: self-referral ─────────────────────────────────────
    if new_user_id == referrer_id:
        logger.warning(f"Self-referral blocked: {new_user_id}")
        return False

    # ── Guard: referrer exists ───────────────────────────────────
    referrer = await get_user(referrer_id)
    if not referrer:
        logger.warning(f"Referrer {referrer_id} not found in DB")
        return False

    # ── Credit the referrer ──────────────────────────────────────
    await increment_referral(referrer_id)
    new_count = referrer["referral_count"] + 1
    new_limit = referrer["daily_video_limit"] + REFERRAL_BONUS

    logger.info(
        f"Referral OK: {new_user_id} → referrer {referrer_id} "
        f"(now {new_count} refs, limit {new_limit})"
    )

    # ── Notify the referrer ──────────────────────────────────────
    try:
        await client.send_message(
            referrer_id,
            f"<b>🎉 New Referral!</b>\n\n"
            f"A new user joined using your link.\n"
            f"<b>+{REFERRAL_BONUS}</b> videos added to your daily limit!\n\n"
            f"<b>👥 Total Referrals:</b> {new_count}\n"
            f"<b>📹 New Daily Limit:</b> {new_limit}",
        )
    except Exception as e:
        logger.error(f"Could not notify referrer {referrer_id}: {e}")

    return True
