import sqlite3
import datetime
from config import DB_NAME, DEFAULT_COOLDOWN, DEFAULT_VIP_PRICE, VIP_PAYMENT_INFO

def get_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                lang TEXT DEFAULT 'uz',
                gender TEXT,
                age_group TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_vip INTEGER DEFAULT 0,
                vip_expire TIMESTAMP,
                last_download_time TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE,
                title TEXT,
                username TEXT,
                invite_link TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('op_enabled', '1')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('cooldown_seconds', ?)", (str(DEFAULT_COOLDOWN),))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('vip_price', ?)", (str(DEFAULT_VIP_PRICE),))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('vip_payment_info', ?)", (VIP_PAYMENT_INFO,))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('total_downloads', '0')")

        conn.commit()

def get_user(telegram_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()

def add_or_update_user(telegram_id: int, username: str, full_name: str, lang='uz', gender=None, age_group=None, country=None):
    with get_db() as conn:
        cursor = conn.cursor()
        existing = get_user(telegram_id)
        now = datetime.datetime.now().isoformat()
        if existing:
            cursor.execute('''
                UPDATE users 
                SET username = ?, full_name = ?, last_active = ?,
                    lang = COALESCE(?, lang),
                    gender = COALESCE(?, gender),
                    age_group = COALESCE(?, age_group),
                    country = COALESCE(?, country)
                WHERE telegram_id = ?
            ''', (username, full_name, now, lang, gender, age_group, country, telegram_id))
        else:
            cursor.execute('''
                INSERT INTO users (telegram_id, username, full_name, lang, gender, age_group, country, created_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, username, full_name, lang, gender, age_group, country, now, now))
        conn.commit()

def set_user_profile(telegram_id: int, lang: str, gender: str, age_group: str, country: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET lang = ?, gender = ?, age_group = ?, country = ? WHERE telegram_id = ?
        ''', (lang, gender, age_group, country, telegram_id))
        conn.commit()

def is_user_vip(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    if not user or not user['is_vip']:
        return False
    if user['vip_expire']:
        try:
            expire_dt = datetime.datetime.fromisoformat(user['vip_expire'])
            if datetime.datetime.now() > expire_dt:
                set_vip_status(telegram_id, False)
                return False
        except Exception:
            return False
    return True

def set_vip_status(telegram_id: int, is_vip: bool, days: int = 30):
    with get_db() as conn:
        cursor = conn.cursor()
        if is_vip:
            expire_dt = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
            cursor.execute("UPDATE users SET is_vip = 1, vip_expire = ? WHERE telegram_id = ?", (expire_dt, telegram_id))
        else:
            cursor.execute("UPDATE users SET is_vip = 0, vip_expire = NULL WHERE telegram_id = ?", (telegram_id,))
        conn.commit()

def update_last_download(telegram_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().isoformat()
        cursor.execute("UPDATE users SET last_download_time = ? WHERE telegram_id = ?", (now, telegram_id))
        cursor.execute("UPDATE settings SET value = CAST(value AS INTEGER) + 1 WHERE key = 'total_downloads'")
        conn.commit()

def get_channels():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM channels")
        return cursor.fetchall()

def add_channel(channel_id: str, title: str, username: str, invite_link: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO channels (channel_id, title, username, invite_link) VALUES (?, ?, ?, ?)",
                       (channel_id, title, username, invite_link))
        conn.commit()

def remove_channel(channel_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM channels WHERE channel_id = ? OR username = ?", (channel_id, channel_id))
        conn.commit()

def get_setting(key: str, default=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else default

def set_setting(key: str, value: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()

def get_overall_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_vip = 1")
        total_vips = cursor.fetchone()['total']

        cursor.execute("SELECT value FROM settings WHERE key = 'total_downloads'")
        row = cursor.fetchone()
        total_downloads = row['value'] if row else 0

        cursor.execute("SELECT country, COUNT(*) as count FROM users WHERE country IS NOT NULL GROUP BY country ORDER BY count DESC LIMIT 15")
        countries = cursor.fetchall()

        cursor.execute("SELECT gender, COUNT(*) as count FROM users WHERE gender IS NOT NULL GROUP BY gender")
        genders = cursor.fetchall()

        return {
            "total_users": total_users,
            "total_vips": total_vips,
            "total_downloads": total_downloads,
            "countries": countries,
            "genders": genders
        }

def get_target_users(country=None, gender=None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT telegram_id FROM users WHERE 1=1"
        params = []
        if country:
            query += " AND country = ?"
            params.append(country)
        if gender:
            query += " AND gender = ?"
            params.append(gender)
        cursor.execute(query, params)
        return [row['telegram_id'] for row in cursor.fetchall()]
