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

# ✅ Initialize only (DO NOT call application.start())
loop.run_until_complete(application.initialize())

# ✅ Reset and set webhook cleanly
loop.run_until_complete(
    application.bot.delete_webhook(drop_pending_updates=True)
)

loop.run_until_complete(
    application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
)

print("✅ Webhook configured")


@app.route("/")
def index():
    return "Bot is running ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        # ✅ Directly run coroutine
        loop.run_until_complete(application.process_update(update))

        return jsonify({"ok": True})
    except Exception as e:
        print("🔥 Webhook error:", e)
        return jsonify({"ok": False}), 200
