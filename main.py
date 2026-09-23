import os
import sys

# Ensure root directory is on Python path for Linux imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from aiohttp import web

# Ensure static ffmpeg is on system PATH
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception as e:
    print(f"static_ffmpeg notice: {e}")

# Ensure UTF-8 output encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from middlewares.throttling import ThrottlingMiddleware
from handlers import start, vip, admin, downloader

logging.basicConfig(level=logging.INFO)

async def handle_health(request):
    return web.Response(text="OK - Bot is running")

async def start_dummy_server():
    """Starts a lightweight HTTP server to satisfy Render Web Service port scanning."""
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Render HTTP Port listener active on port {port}")

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ XATO: .env faylida BOT_TOKEN ko'rsatilmagan! Iltimos, Tokeningizni joylang.")
        return

    # Initialize SQLite database
    init_db()

    # Start dummy HTTP listener for Render port check
    try:
        await start_dummy_server()
    except Exception as e:
        print(f"HTTP Server notice: {e}")

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
