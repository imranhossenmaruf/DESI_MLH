"""
Async MongoDB database layer using Motor.
Handles users collection, videos collection, and all CRUD operations.
"""

import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, DEFAULT_DAILY_LIMIT

logger = logging.getLogger("DATABASE")

# ─── Connection ──────────────────────────────────────────────────
client = AsyncIOMotorClient(MONGO_URL)
db = client["telegram_video_bot"]
users_col = db["users"]
videos_col = db["videos"]


# ─── Initialization ─────────────────────────────────────────────
async def init_db():
    """Create indexes for optimal query performance."""
    await users_col.create_index("user_id", unique=True)
    await videos_col.create_index("file_id", unique=True)
    logger.info("Database indexes ensured")


# ═══════════════════════════════════════════════════════════════
#  USER OPERATIONS
# ═══════════════════════════════════════════════════════════════

async def add_user(
    user_id: int,
    first_name: str,
    username: str,
    referred_by: int = None,
) -> bool:
    """
    Insert a new user. Returns True if newly created, False if already exists.
    """
    existing = await users_col.find_one({"user_id": user_id})
    if existing:
        # Update name/username in case they changed
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"first_name": first_name, "username": username}},
        )
        return False

    user_doc = {
        "user_id": user_id,
        "first_name": first_name,
        "username": username,
        "join_date": datetime.utcnow(),
        "referred_by": referred_by,
        "referral_count": 0,
        "daily_video_limit": DEFAULT_DAILY_LIMIT,
        "today_video_used": 0,
        "last_reset_date": datetime.utcnow().strftime("%Y-%m-%d"),
    }
    await users_col.insert_one(user_doc)
    logger.info(f"New user added: {user_id} ({first_name})")
    return True


async def get_user(user_id: int) -> dict | None:
    return await users_col.find_one({"user_id": user_id})


async def get_all_user_ids() -> list[int]:
    cursor = users_col.find({}, {"user_id": 1, "_id": 0})
    return [doc["user_id"] async for doc in cursor]


async def update_user(user_id: int, data: dict):
    await users_col.update_one({"user_id": user_id}, {"$set": data})


async def increment_referral(user_id: int):
    """Add +1 referral count and +REFERRAL_BONUS to daily limit."""
    from config import REFERRAL_BONUS
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"referral_count": 1, "daily_video_limit": REFERRAL_BONUS}},
    )
    logger.info(f"Referral incremented for {user_id}")


async def check_and_reset_daily(user_id: int):
    """Reset a single user's daily counter if the date has changed."""
    user = await get_user(user_id)
    if not user:
        return
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user.get("last_reset_date") != today:
        await update_user(user_id, {"today_video_used": 0, "last_reset_date": today})


async def increment_video_used(user_id: int):
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"today_video_used": 1}},
    )


# ═══════════════════════════════════════════════════════════════
#  VIDEO OPERATIONS
# ═══════════════════════════════════════════════════════════════

async def add_video(file_id: str, added_by: int) -> bool:
    """Add a video. Returns False if duplicate."""
    existing = await videos_col.find_one({"file_id": file_id})
    if existing:
        return False
    await videos_col.insert_one(
        {"file_id": file_id, "added_by": added_by, "added_date": datetime.utcnow()}
    )
    logger.info(f"Video added by {added_by}")
    return True


async def get_random_video() -> dict | None:
    """Return one random video document, or None."""
    async for doc in videos_col.aggregate([{"$sample": {"size": 1}}]):
        return doc
    return None


async def get_total_videos() -> int:
    return await videos_col.count_documents({})


# ═══════════════════════════════════════════════════════════════
#  STATISTICS
# ═══════════════════════════════════════════════════════════════

async def get_total_users() -> int:
    return await users_col.count_documents({})


async def get_users_last_7_days() -> dict[str, int]:
    """Return {date_string: new_user_count} for the last 7 days."""
    results = {}
    for i in range(7):
        day = datetime.utcnow() - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        start = datetime.strptime(day_str, "%Y-%m-%d")
        end = start + timedelta(days=1)
        count = await users_col.count_documents(
            {"join_date": {"$gte": start, "$lt": end}}
        )
        results[day_str] = count
    return results


# ═══════════════════════════════════════════════════════════════
#  BULK RESET (background task)
# ═══════════════════════════════════════════════════════════════

async def bulk_reset_daily() -> int:
    """Reset daily usage for all users whose date is stale. Returns count."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    result = await users_col.update_many(
        {"last_reset_date": {"$ne": today}},
        {"$set": {"today_video_used": 0, "last_reset_date": today}},
    )
    return result.modified_count
