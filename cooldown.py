import datetime
from database import is_user_vip, get_user, get_setting

def check_user_cooldown(telegram_id: int):
    """
    Returns (can_download: bool, wait_seconds_left: int)
    VIP users always get (True, 0).
    Free users must wait cooldown_seconds between downloads.
    """
    if is_user_vip(telegram_id):
        return True, 0

    user = get_user(telegram_id)
    if not user or not user['last_download_time']:
        return True, 0

    try:
        last_dt = datetime.datetime.fromisoformat(user['last_download_time'])
    except Exception:
        return True, 0

    cooldown_sec = int(get_setting('cooldown_seconds', '90'))
    elapsed = (datetime.datetime.now() - last_dt).total_seconds()

    if elapsed >= cooldown_sec:
        return True, 0
    else:
        left = int(cooldown_sec - elapsed)
        return False, left
