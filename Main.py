import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- بخش اول: سرور بیدار نگه داشتن ربات ---
app = Flask(__name__)
@app.route('/')
def home():
    return "ربات گفتاردرمانی ترنم فعال است!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- بخش دوم: تنظیمات هوش مصنوعی و تلگرام ---
# کلید جمینای خود را دقیقاً بین دو کوتیشن زیر قرار دهید:
genai.configure(api_key="کلید_جمینای_شما")

system_instruction = """
شما دستیار هوشمند مرکز گفتاردرمانی ترنم هستید. وظیفه شما راهنمایی مادران در زمینه رشد زبانی کودکان است.
لحن شما مهربان و ساده است. فقط بر اساس اصول علمی گفتاردرمانی پاسخ دهید و برای تشخیص دقیق، مادران را به ارزیابی حضوری در اهواز ارجاع دهید.
"""
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

# رمز عبور ورود والدین به ربات:
VIP_PASSWORD = "tala"
authenticated_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authenticated_users:
        await update.message.reply_text("سلام مادر عزیز! به دستیار هوشمند مرکز ترنم خوش آمدید.\nلطفاً برای استفاده از ربات، رمز عبور دوره را ارسال کنید:")
    else:
        await update.message.reply_text("شما قبلاً وارد شده‌اید. سوال خود را بپرسید.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in authenticated_users:
        if user_text == VIP_PASSWORD:
            authenticated_users.add(user_id)
            await update.message.reply_text("رمز عبور صحیح بود! حالا می‌توانید دغدغه‌ها و سوالات خود را بپرسید.")
        else:
            await update.message.reply_text("رمز عبور اشتباه است. لطفاً رمز صحیح را وارد کنید.")
        return

    await update.message.reply_text("در حال بررسی...")
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("خطایی رخ داد. لطفاً دوباره تلاش کنید.")

def main():
    # توکن ربات تلگرام خود را دقیقاً بین دو کوتیشن زیر قرار دهید:
    application = Application.builder().token("توکن_تلگرام_شما").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    keep_alive()
    application.run_polling()

if __name__ == '__main__':
    main()
