# 🎬 Desi MLH Telegram Bot

A powerful Pyrogram-based Telegram bot for video sharing with a referral system, auto-approval, and admin controls.

## 🚀 Features
- ✅ **Auto-Approve:** Automatically accepts join requests.
- 👥 **Referral System:** Users earn +5 daily limit per referral.
- 📹 **Video Database:** Random video delivery from a specific channel.
- 📊 **Statistics:** Track users, active status, and usage.
- 📢 **Broadcast:** Admin can send messages to all users.
- 🛡️ **Security:** Prevents link sharing and forwarding in groups.

## 🛠 Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/desi-mlh-bot.git
   cd desi-mlh-bot
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file (use `.env.example` as a template).

4. **Run the Bot:**
   ```bash
   python bot.py
   ```

## 📝 Environment Variables
- `API_ID`: Get from my.telegram.org
- `API_HASH`: Get from my.telegram.org
- `BOT_TOKEN`: Get from @BotFather
- `MONGO_URL`: Your MongoDB connection string
- `LOG_GROUP_ID`: ID of your log group
- `DATABASE_CHANNEL_ID`: ID of the channel where videos are stored
- `ADMIN_ID`: Your Telegram User ID
