import sys
import asyncio
import logging

# Ensure UTF-8 output encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from middlewares.throttling import ThrottlingMiddleware
from handlers import start, vip, admin, downloader

logging.basicConfig(level=logging.INFO)

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ XATO: .env faylida BOT_TOKEN ko'rsatilmagan! Iltimos, Tokeningizni joylang.")
        return

    # Initialize SQLite database
    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Clear any previous webhook to enable polling mode
    await bot.delete_webhook(drop_pending_updates=True)

    # Register Throttling Middleware
    dp.message.middleware(ThrottlingMiddleware(rate_limit=2.0))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=1.5))

    # Register Handlers
    dp.include_router(start.router)
    dp.include_router(vip.router)
    dp.include_router(admin.router)
    dp.include_router(downloader.router)

    print("🚀 Telegram Media Downloader Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")
