import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in ADMIN_IDS_RAW.split(",") if i.strip().isdigit()]

DB_NAME = os.getenv("DB_NAME", "bot.db")
DEFAULT_COOLDOWN = int(os.getenv("DEFAULT_COOLDOWN", "90"))
DEFAULT_VIP_PRICE = int(os.getenv("DEFAULT_VIP_PRICE", "20000"))
VIP_PAYMENT_INFO = os.getenv("VIP_PAYMENT_INFO", "8600 0000 0000 0000 (UzCard/Humo)")

# Allowed domains for video downloading
ALLOWED_DOMAINS = [
    "instagram.com", "instagr.am",
    "tiktok.com", "vt.tiktok.com", "vm.tiktok.com",
    "youtube.com", "youtu.be",
    "pinterest.com", "pin.it"
]
