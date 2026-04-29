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
    print("✅ /start triggered")
    active_users[update.effective_user.id] = True
    await update.message.reply_text("✅ Bot is alive and listening!")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_users[update.effective_user.id] = False
    await update.message.reply_text("🛑 Standby mode activated.")


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        f"✅ Bot Status: Healthy\n\nAPI Usage:\n{api_usage}"
    )

# ==========================
# MAIN MESSAGE HANDLER
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        if not update.message:
            print("❌ No message in update")
            return

        if not update.message.text:
            print("❌ No text in message")
            return

        user_id = update.effective_user.id

        if not active_users.get(user_id, True):
            print("User in standby mode")
            return

        text = update.message.text
        print("📩 Received:", text)

        lang = detect_language(text)

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

        # ✅ Always ensure reply exists
        if not reply:
            reply = "I couldn't generate a response."

        # ✅ SEND TEXT
        await update.message.reply_text(reply)

        # ✅ SEND VOICE
        try:
            voice_path = generate_voice(reply, lang)
            with open(voice_path, "rb") as audio:
                await update.message.reply_voice(audio)
        except Exception as voice_error:
            print("⚠ Voice generation failed:", voice_error)

    except Exception as e:
        print("🔥 Handler crashed:", e)
        try:
            await update.message.reply_text("⚠ Something went wrong.")
        except:
            pass


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
