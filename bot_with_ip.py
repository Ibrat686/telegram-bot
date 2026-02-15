import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8429666405:AAE1E9uCsO1kckVPlGYi7XDH75aCqi8VKvo"
PUBLIC_URL = "https://telegram-bot-u5fe.onrender.com"  # потом заменишь

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Сервер работает 🎉</h1>
    <p>Бот онлайн 24/7</p>
    """

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)

# ================= TELEGRAM =================
async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 ОТКРЫТЬ ССЫЛКУ", url=PUBLIC_URL)]
    ])

    await update.message.reply_text(
        "👇 Нажми кнопку чтобы открыть ссылку:",
        reply_markup=keyboard
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_link(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_link(update, context)

def run_bot():
    try:
        bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        print("🤖 Telegram бот запущен")
        bot_app.run_polling()
    except Exception as e:
        print("❌ Ошибка бота:", e)

# ================= ЗАПУСК =================
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    run_bot()
