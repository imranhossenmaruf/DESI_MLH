from pyrogram import Client, filters
from systems.leaderboard import get_leaderboard


@Client.on_message(filters.command("leaderboard"))
async def leaderboard_command(client, message):

    data = await get_leaderboard()

    text = "🏆 Leaderboard\n\n"

    for i, user in enumerate(data, start=1):
        text += f"{i}. {user['name']} - {user['points']}\n"

    await message.reply(text)