import os
from flask import Flask, request, jsonify
from telegram import Update
from bot import setup_bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
application = setup_bot(TELEGRAM_TOKEN)

@app.route("/")
def index():
    return jsonify({"status": "Bot running ✅"})

@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return jsonify({"ok": True})

@app.route("/setwebhook")
def set_webhook():
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/webhook"
    r = requests.post(url, json={"url": webhook_url})
    return r.json()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
