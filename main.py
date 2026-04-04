import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-3.5-turbo"
MY_ID = 8475704328

async def get_ai_reply(text: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": text}],
        "temperature": 0.7
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    return "Sorry, I cannot reply right now."
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return "Sorry, I cannot reply right now."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return

    bot_id = context.bot.id
    trigger = False

    if msg.entities:
        for entity in msg.entities:
            if entity.type == "mention" and entity.user:
                if entity.user.id == MY_ID or entity.user.id == bot_id:
                    trigger = True

    if msg.reply_to_message:
        replied_id = msg.reply_to_message.from_user.id
        if replied_id == MY_ID or replied_id == bot_id:
            trigger = True

    if not trigger:
        return

    reply = await get_ai_reply(msg.text)
    await msg.reply_text(reply)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
