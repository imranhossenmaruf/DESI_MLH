from pyrogram import Client, idle
import config


class Bot(Client):

    def __init__(self):

        super().__init__(
            name="TelegramBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="plugins")  # plugins folder auto load
        )


# Bot instance
app = Bot()


async def main():

    await app.start()

    me = await app.get_me()

    print("=================================")
    print(f"Bot Started : {me.first_name}")
    print(f"Bot Username : @{me.username}")
    print("=================================")

    await idle()

    await app.stop()


if __name__ == "__main__":
    app.run(main())