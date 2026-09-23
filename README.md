# Telegram Media Downloader & Monetization Bot 🚀

Bu bot Instagram Reels, TikTok, YouTube Shorts/Videos va Pinterest loyihalaringizdan videolarni suv belgisiz yuklovchi, videolardan `Shazam` orqali to'liq MP3 qo'shiqlarni izlab topuvchi hamda **Majburiy Obuna (OP)**, **Geotargeted Reklama** va **VIP Obuna** orqali yuqori daromad keltiruvchi Telegram botidir.

---

## 📂 Loyiha Fayllari Tuzilishi

* `main.py` — Botni ishga tushirish asosiy fayli.
* `.env` — Bot Token va Admin ID kabi maxfiy sozlamalar fayli.
* `config.py` — Bot sozlamalarini yuklovchi fayl.
* `database.py` — SQLite shifrlangan va xavfsiz ma'lumotlar bazasi.
* `requirements.txt` — Bot uchun kerakli kutubxonalar (aiogram 3.x, yt-dlp, shazamio).
* `handlers/` — Botning mantiqiy bo'limlari (start, downloader, vip, admin).
* `middlewares/` — Anti-Flood (Throttling), Cooldown va Majburiy Obuna (OP) himoya qatlamlari.
* `services/` — Video va Shazam MP3 yuklash xizmatlari.

---

## 🛠️ SERVERGA O'RNATISH VA ISHGA TUSHIRISH (BOSQICHMA-BOSQICH)

### 1-qadam: `.env` faylini sozlash
`.env` faylini oching va quyidagi ma'lumotlarni o'zingizniki bilan almashtiring:
```env
BOT_TOKEN=8123456789:AAEF... (BotFather'dan olingan token)
ADMIN_IDS=123456789 (O'zingizning Telegram ID'ingiz)
DEFAULT_COOLDOWN=90 (Oddiy foydalanuvchilar kutish vaqti - soniyada)
DEFAULT_VIP_PRICE=20000 (VIP oylik narxi)
VIP_PAYMENT_INFO=8600 0000 0000 0000 (Karta raqamingiz)
```
*(Telegram ID'ingizni bilish uchun Telegramda @userinfobot ga yozing).*

### 2-qadam: Kutubxonalarni o'rnatish
Linux (Ubuntu/Debian) VPS serverda quyidagi buyruqlarni ketma-ket kiriting:
```bash
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg
pip install -r requirements.txt
```
*(Eslatma: FFmpeg videolardan audio qirqib olish va Shazam uchun zarur).*

### 3-qadam: Botni 24/7 rejimda ishga tushirish (pm2 yoki systemd yordamida)

**A) PM2 yordamida (Tavsiya etiladi):**
```bash
sudo apt install -y npm
sudo npm install -y pm2 -g
pm2 start main.py --name "media_downloader_bot" --interpreter python3
pm2 save
pm2 startup
```

**B) Oddiy test tarzida ishga tushirish:**
```bash
python3 main.py
```

---

## 👑 ADMIN PANEL IMKONIYATLARI
Botga admin sifatida `/admin` deb yozsangiz, quyidagi tugmalar chiqadi:
* **📢 Majburiy Obuna (OP):** Homiy kanallar obunasini 1 ta tugma bilan **Yoqish/O'chirish**.
* **➕/➖ Kanal Boshqaruv:** Homiy kanallarni qo'shish va o'chirish.
* **🎯 Segmentlangan Reklama:** Reklamalarni barcha foydalanuvchilarga yoki faqat ma'lum bir **Mamlakat** (O'zbekiston, Rossiya va h.k.) yoki **Jins** foydalanuvchilariga maqsadli yuborish.
* **📊 Statistikalar:** Mamlakatlar va jins bo'yicha batafsil hisobotlar.
* **💰 VIP Narxlari va ⏳ Cooldown:** Narxlarni va kutish vaqtlarini dinamik o'zgartirish.
