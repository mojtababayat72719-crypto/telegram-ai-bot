import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai
import requests

# تنظیمات لاگ‌گیری برای دیدن خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. تنظیم کلیدهای API (بعداً این‌ها را با کلیدهای واقعی خودت جایگزین می‌کنی)
TELEGRAM_BOT_TOKEN = "TOKEN_KHOD_RA_ENJA_BEZAR"
GEMINI_API_KEY = "GEMINI_KEY_KHOD_RA_ENJA_BEZAR"
HUGGINGFACE_API_KEY = "HF_KEY_KHOD_RA_ENJA_BEZAR"

# راه‌اندازی جمنای برای بخش چت
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# آدرس API مدل Stable Diffusion روی هاگینگ‌فیس
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# دستور شروع /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_message = (
        f"سلام {user_name} عزیز! 🤖\n\n"
        "من ربات هوش مصنوعی شما هستم:\n"
        "💬 **چت:** هر سوالی داری از من بپرس.\n"
        "🎨 **ساخت عکس:** کافیه اول دستورت کلمه 'عکس:' یا 'image:' را بنویسی تا برات عکس بسازم.\n\n"
        "بیا شروع کنیم!"
    )
    await update.message.reply_text(welcome_message)

# مدیریت پیام‌های متنی و ساخت عکس
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if user_text.lower().startswith("عکس:") or user_text.lower().startswith("image:"):
        prompt = user_text.split(":", 1)[1].strip()
        await update.message.reply_text("⏳ در حال پردازش و ساخت تصویر، لطفاً چند لحظه صبر کنید...")
        
        try:
            response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                await update.message.reply_photo(photo=response.content, caption=f"✨ پرامپت: {prompt}")
            else:
                await update.message.reply_text("❌ متأسفانه در ساخت عکس خطایی رخ داد یا سرور شلوغ است. دوباره تلاش کنید.")
        except Exception as e:
            await update.message.reply_text("❌ خطا در اتصال به سرویس ساخت تصویر.")
            
    else:
        try:
            chat_response = gemini_model.generate_content(user_text)
            await update.message.reply_text(chat_response.text)
        except Exception as e:
            await update.message.reply_text("❌ متأسفانه در پاسخ‌دهی خطایی رخ داد.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 ربات با موفقیت روشن شد و در حال گوش دادن است...")
    app.run_polling()

if __name__ == '__main__':
    main()
