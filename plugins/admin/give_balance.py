from pyrogram import Client, filters
from config import ADMIN_IDS
from systems.economy import add_balance


@Client.on_message(filters.command("givebalance") & filters.user(ADMIN_IDS))
async def give_balance(client, message):

    if len(message.command) < 3:
        return await message.reply(
            "Usage:\n/givebalance user_id amount"
        )

    user_id = int(message.command[1])
    amount = int(message.command[2])

    await add_balance(user_id, amount)

    await message.reply("✅ Balance Added")