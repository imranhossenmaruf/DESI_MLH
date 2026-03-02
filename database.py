import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import random

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["desi_mlh_db"]
users = db["users"]
videos = db["videos"]

async def add_user(user_id, first_name, username, referred_by=None):
    user = await users.find_one({"user_id": user_id})
    if not user:
        await users.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "join_date": datetime.now(),
            "ref_count": 0,
            "daily_limit": 10,
            "today_used": 0,
            "last_reset": datetime.now(),
            "referred_by": referred_by,
            "is_blocked": False
        })
        return True
    return False

async def get_user(user_id):
    return await users.find_one({"user_id": user_id})

async def update_user(user_id, data):
    await users.update_one({"user_id": user_id}, {"$set": data})

async def add_video(file_id):
    if not await videos.find_one({"file_id": file_id}):
        await videos.insert_one({"file_id": file_id})

async def get_random_video():
    all_vids = await videos.find().to_list(length=None)
    if all_vids:
        return random.choice(all_vids)["file_id"]
    return None

async def get_total_users_count():
    return await users.count_documents({})

async def get_blocked_users_count():
    return await users.count_documents({"is_blocked": True})

async def get_all_users():
    return users.find({})
