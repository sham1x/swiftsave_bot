from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_setting, get_channels, is_user_vip

async def check_user_subscriptions(bot, user_id: int) -> tuple[bool, InlineKeyboardMarkup]:
    """
    Checks if user is subscribed to all mandatory channels if OP is enabled.
    Returns (is_subscribed: bool, markup_with_links: InlineKeyboardMarkup).
    VIP users bypass mandatory subscription!
    """
    # If VIP user, bypass OP
    if is_user_vip(user_id):
        return True, None

    # Check if OP is enabled in admin settings
    op_enabled = get_setting('op_enabled', '1')
    if op_enabled != '1':
        return True, None

    channels = get_channels()
    if not channels:
        return True, None

    unsubscribed_buttons = []
    all_subscribed = True

    for ch in channels:
        channel_id = ch['channel_id']
        invite_link = ch['invite_link'] or f"https://t.me/{ch['username'].replace('@', '')}"
        title = ch['title'] or "Homiy kanal"

        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ['left', 'kicked']:
                all_subscribed = False
                unsubscribed_buttons.append([InlineKeyboardButton(text=f"➕ {title}", url=invite_link)])
        except Exception:
            # In case bot cannot check chat member (e.g. invalid channel ID or bot not admin)
            pass

    if not all_subscribed:
        unsubscribed_buttons.append([InlineKeyboardButton(text="✅ Obunani Tekshirish", callback_data="check_subscription")])
        markup = InlineKeyboardMarkup(inline_keyboard=unsubscribed_buttons)
        return False, markup

    return True, None
