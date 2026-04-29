import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from bot import setup_bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)

# ✅ Create dedicated asyncio event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

application = setup_bot(TELEGRAM_TOKEN)

# ✅ Initialize telegram application properly
loop.run_until_complete(application.initialize())
loop.run_until_complete(application.start())


@app.route("/")
def index():
    return "Bot is running ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        # ✅ Run async processing inside our loop
        loop.create_task(application.process_update(update))

        return jsonify({"ok": True})
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"ok": False}), 200


@app.route("/shutdown")
def shutdown():
    loop.run_until_complete(application.stop())
    return "Shutting down..."
