import time
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 2.0):
        super().__init__()
        self.rate_limit = rate_limit
        self.user_last_msg = {}
        self.last_cleanup = time.time()

    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        now = time.time()

        # Periodic memory cleanup every 10 minutes
        if now - self.last_cleanup > 600:
            self.user_last_msg = {u: t for u, t in self.user_last_msg.items() if now - t < 60}
            self.last_cleanup = now

        if user_id:
            last_time = self.user_last_msg.get(user_id, 0)
            if now - last_time < self.rate_limit:
                if isinstance(event, Message):
                    await event.answer("Juda tez so'rov yubormang. Bir oz kuting!")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Juda tez tugma bosdingiz!", show_alert=True)
                return
            self.user_last_msg[user_id] = now

        return await handler(event, data)
