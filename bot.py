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

from services.llm import ask_llm
from services.voice import generate_voice
from services.language import detect_language
from services.search import wikipedia_search, get_news, web_search

OWNER_ID = int(os.getenv("OWNER_ID", "733340342"))

active_users = {}
api_usage = {
    "llm": 0,
    "wiki": 0,
    "news": 0,
    "search": 0,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_users[update.effective_user.id] = True
    await update.message.reply_text("✅ Listening... Send /stop to pause.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_users[update.effective_user.id] = False
    await update.message.reply_text("🛑 Standby mode activated.")

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(f"✅ Bot healthy\n\nAPI Usage:\n{api_usage}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not active_users.get(user_id, True):
        return

    text = update.message.text
    lang = detect_language(text)

    if "news" in text.lower():
        api_usage["news"] += 1
        reply = get_news()
    elif "who is" in text.lower():
        api_usage["wiki"] += 1
        reply = wikipedia_search(text.replace("who is", ""))
    elif "search" in text.lower():
        api_usage["search"] += 1
        reply = web_search(text.replace("search", ""))
    else:
        api_usage["llm"] += 1
        reply = ask_llm(text)

    await update.message.reply_text(reply)

    voice_path = generate_voice(reply, lang)
    with open(voice_path, "rb") as audio:
        await update.message.reply_voice(audio)

def setup_bot(token):
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler(["stop", "bye", "standby"], stop))
    application.add_handler(CommandHandler("health", health))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application
