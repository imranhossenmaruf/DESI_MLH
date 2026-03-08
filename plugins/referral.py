from pyrogram import Client, filters
from systems.referral import get_referrals


@Client.on_message(filters.command("referral"))
async def referral_command(client, message):

    user_id = message.from_user.id

    referrals = await get_referrals(user_id)

    await message.reply(
        f"👥 Your Referrals : {referrals}"
    )