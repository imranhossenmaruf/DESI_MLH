from database import get_user, increment_user, update_user


async def process_referral(new_user_id, referrer_id):
    if new_user_id == referrer_id:
        return

    referrer = await get_user(referrer_id)
    new_user = await get_user(new_user_id)

    if not referrer:
        return

    if new_user.get("referred_by"):
        return

    await increment_user(referrer_id, "referral_count", 1)
    await increment_user(referrer_id, "daily_video_limit", 5)
    await update_user(new_user_id, {"referred_by": referrer_id})
