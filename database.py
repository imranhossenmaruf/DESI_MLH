from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client.video_referral_bot

users = db.users
videos = db.videos


async def add_user(data):
    if not await users.find_one({"user_id": data["user_id"]}):
        await users.insert_one(data)


async def get_user(user_id):
    return await users.find_one({"user_id": user_id})


async def update_user(user_id, data):
    await users.update_one({"user_id": user_id}, {"$set": data})


async def increment_user(user_id, field, value):
    await users.update_one({"user_id": user_id}, {"$inc": {field: value}})


async def total_users():
    return await users.count_documents({})
