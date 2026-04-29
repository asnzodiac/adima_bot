import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from bot import setup_bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

application = setup_bot(TELEGRAM_TOKEN)

# ✅ Proper startup
loop.run_until_complete(application.initialize())

# ✅ Clear old webhook
loop.run_until_complete(
    application.bot.delete_webhook(drop_pending_updates=True)
)

# ✅ SET webhook again automatically
loop.run_until_complete(
    application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
)

loop.run_until_complete(application.start())


@app.route("/")
def index():
    return "Bot is running ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        loop.create_task(application.process_update(update))
        return jsonify({"ok": True})
    except Exception as e:
        print("🔥 Webhook error:", e)
        return jsonify({"ok": False}), 200
