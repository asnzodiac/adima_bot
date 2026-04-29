import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from services.llm_router import ask_llm
from services.voice import generate_voice
from services.language import detect_language
from services.search import wikipedia_search, get_news, web_search
from services.weather import get_weather

# ==========================
# CONFIG
# ==========================

OWNER_ID = int(os.getenv("OWNER_ID", "733340342"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================
# MEMORY STATE
# ==========================

active_users = {}
api_usage = {
    "llm": 0,
    "weather": 0,
    "news": 0,
    "wiki": 0,
    "search": 0,
}

# ==========================
# COMMANDS
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_users[user_id] = True

    await update.message.reply_text(
        "✅ I am now listening.\n\n"
        "Send /stop to enter standby mode."
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_users[user_id] = False

    await update.message.reply_text(
        "🛑 Standby mode activated.\n"
        "Send /start to resume."
    )

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "✅ Bot Status: Healthy\n\n"
        f"API Usage:\n{api_usage}"
    )

# ==========================
# MAIN MESSAGE HANDLER
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # If user in standby mode → ignore
    if not active_users.get(user_id, True):
        return

    text = update.message.text
    lang = detect_language(text)

    try:
        # ===== SMART ROUTING =====

        if "weather" in text.lower():
            api_usage["weather"] += 1
            reply = get_weather()

        elif "news" in text.lower():
            api_usage["news"] += 1
            reply = get_news()

        elif "who is" in text.lower():
            api_usage["wiki"] += 1
            query = text.lower().replace("who is", "").strip()
            reply = wikipedia_search(query)

        elif "search" in text.lower():
            api_usage["search"] += 1
            query = text.lower().replace("search", "").strip()
            reply = web_search(query)

        else:
            api_usage["llm"] += 1
            reply = ask_llm(text)

        # ===== SEND TEXT =====
        await update.message.reply_text(reply)

        # ===== SEND VOICE =====
        voice_path = generate_voice(reply, lang)

        with open(voice_path, "rb") as audio:
            await update.message.reply_voice(audio)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠ Something went wrong. Please try again.")

# ==========================
# SETUP FUNCTION
# ==========================

def setup_bot(token: str):
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler(["stop", "bye", "standby"], stop))
    application.add_handler(CommandHandler("health", health))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    return application
