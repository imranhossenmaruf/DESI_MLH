"""
Configuration module - loads settings from environment variables.
Railway.app compatible — set all values in Railway Variables tab.
"""

import os
import logging

# ─── Logging Setup ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-18s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("CONFIG")

# ─── Telegram API ────────────────────────────────────────────────
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ─── MongoDB ─────────────────────────────────────────────────────
MONGO_URL = os.environ.get("MONGO_URL", "")

# ─── Admin IDs (comma-separated) ────────────────────────────────
_raw_admins = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = [
    int(x.strip())
    for x in _raw_admins.split(",")
    if x.strip().lstrip("-").isdigit()
]

# ─── Log Group ───────────────────────────────────────────────────
LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID", "0"))

# ─── VIP & Contact ──────────────────────────────────────────────
VIP_LINK = os.environ.get("VIP_LINK", "")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")

# ─── Defaults ────────────────────────────────────────────────────
DEFAULT_DAILY_LIMIT = 10          # Videos per day for new users
REFERRAL_BONUS = 5                # Extra videos per successful referral
VIDEO_AUTO_DELETE_SECONDS = 600   # 10 minutes
WARNING_AUTO_DELETE_SECONDS = 20  # 20 seconds

# ─── Validation ──────────────────────────────────────────────────
def validate_config():
    errors = []
    if not API_ID:
        errors.append("API_ID is missing — set it in Railway Variables")
    if not API_HASH:
        errors.append("API_HASH is missing — set it in Railway Variables")
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN is missing — set it in Railway Variables")
    if not MONGO_URL:
        errors.append("MONGO_URL is missing — set it in Railway Variables")
    if not ADMIN_IDS:
        logger.warning("No ADMIN_IDS configured — admin commands disabled")
    if not LOG_GROUP_ID:
        logger.warning("LOG_GROUP_ID not set — logging to group disabled")
    if not VIP_LINK:
        logger.warning("VIP_LINK not set — VIP buttons will be hidden")
    if not ADMIN_USERNAME:
        logger.warning("ADMIN_USERNAME not set")
    if errors:
        for e in errors:
            logger.error(f"❌ Config Error: {e}")
        raise SystemExit(
            "\n\n⚠️  MISSING ENVIRONMENT VARIABLES!\n"
            "Set these in Railway → Your Service → Variables tab:\n"
            "  API_ID, API_HASH, BOT_TOKEN, MONGO_URL\n\n"
        )
    logger.info(f"✅ Config loaded — {len(ADMIN_IDS)} admin(s), log group: {LOG_GROUP_ID}")
    if VIP_LINK:
        logger.info(f"VIP Link: {VIP_LINK}")
    if ADMIN_USERNAME:
        logger.info(f"Admin Contact: @{ADMIN_USERNAME}")
